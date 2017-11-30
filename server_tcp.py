import socket
from structs import *
from signal import signal, SIGTERM, SIGINT
import time
import select
from threading import Thread, Event
import sys

STOP = Event()

class GatewayThread(Thread):
    def __init__(self, gateway, gateway_sock, recv_port, callback):
        Thread.__init__(self)
        self.gateway = gateway
        self.gateway_sock = gateway_sock
        self.recv_port = recv_port
        self.callback = callback

    def run(self):
        '''
        # 1. Tell the gateway who you are
        # 2. Get all clients from gateway
        # 3. send all clients a packet from recv_port
        # 4. monitor gateway for new events
        '''
        print "TCP Server sending ID to Gateway"
        packet = Packet('SERVER')
        packet.payload = ('localhost', self.recv_port)
        self.gateway_sock.sendto(packet.encode(), self.gateway)

        print STOP
        while not STOP.is_set():
            try:
                print "TCP Server waiting on gateway"
                ready = select.select([self.gateway_sock], [], [], 1)
            except:
                raise
            if ready[0]:
                try:
                    print "TCP Server reading from gateway"
                    data, _ = self.gateway_sock.recvfrom(4096)
                except:
                    return
            print "TCP Server received clients list from Gateway"
            packet = Packet.decode(data)
            clients = packet.payload

            for client in clients:
                self.callback(client)


# class AcceptThread(Thread):
#     def __init__(self, accept_sock):
#         self.accept_sock = accept_sock
#
#     def run(self):
#         self.accept_sock.listen(1)
#         self.accept_sock.settimeout(5)
#         while not STOP.is_set():
#             try:
#                 self.conn, addr = self.accept_sock.accept()
#             except socket.timeout:
#                 continue
#             else:
#                 print "Accept connected!"
#                 STOP.set()
#             data = conn.recv(4096)
#             print "Recieved request at server from accepted connection: ", data
#             packet = Packet(SERVER)
#             packet.payload = "Returning some stuffs"
#             self.conn.send(packet.encode())

class ConnectThread(Thread):
    def __init__(self, connect_sock, client):
        Thread.__init__(self)
        self.connect_sock = connect_sock
        self.client = client

    def run(self):
        while not STOP.is_set():
            try:
                self.connect_sock.connect(tuple(self.client))
            except socket.error:
                continue
            else:
                print "connected from --- success!"
                STOP.set()
        data = self.connect_sock.recv(4096)
        print "Recieved request at server from accepted connection: ", data
        packet = Packet(SERVER)
        packet.payload = "Returning some stuffs"
        self.connect_sock.send(packet.encode())

class LCPSocket(object):
    def __init__(self, gateway, tcp=True):
        self.tcp = tcp
        self.gateway = gateway
        self.gthread = None
        # Create 2 sockets
        # gateway_sock -> Communicating with the gateway server
        # server_sock -> socket to get connections from client
        self.gateway_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # self.accept_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # self.accept_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # self.accept_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)

        self.connect_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # self.connect_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # self.connect_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)

    def bind(self, addr):
        # self.accept_sock.bind(addr)
        self.connect_sock.bind( (addr[0], 0) )
        #self.accept_recv_port = self.server_sock.getsockname()[1]# Store this to communicate to gateway
        self.connect_recv_port = self.connect_sock.getsockname()[1]# Store this to communicate to gateway
        print "Server thread adding rcv_port", self.connect_recv_port

    def _trigger_connection(self, client):
        # self.accept_thread = AcceptThread(self.accept_sock)
        self.connect_thread = ConnectThread(self.connect_sock, client)
        # self.accept_thread.start()
        self.connect_thread.start()
        threads = [ self.connect_thread ] # self.accept_thread,
        while len(threads) > 0:
            for thread in threads:
                try:
                    thread.join(1)
                except TimeoutError:
                    continue
                if not thread.is_alive():
                    threads.remove(thread)

    def listen(self, backlog=5):
        # Before we start listening we want to register with the gateway
        # This should be done in a separate thread so it can continue to listen
        # for new events
        # Once that thread is kicked off we can start listening on the recv_port

        self.gateway_thread = GatewayThread(self.gateway, self.gateway_sock, self.connect_recv_port, self._trigger_connection)
        self.gateway_thread.start()
        signal(SIGTERM, self.before_exit)
        signal(SIGINT, self.before_exit)

        while not STOP.is_set():
            time.sleep(1)

    def before_exit(self, *args):
        STOP.set()
        self.gateway_thread.join()
        #self.accept_thread.join()
        self.connect_thread.join()
        sys.exit(-1)

def lambda_handler(event, context):
    sock = LCPSocket((event['ip'], int(event['port'])))
    sock.bind(('0.0.0.0', 0))
    sock.listen()
