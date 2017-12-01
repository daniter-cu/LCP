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
        packet = Packet('CLIENT')
        packet.payload = ('localhost', self.recv_port)
        self.gateway_sock.connect(self.gateway)
        self.gateway_sock.send(packet.encode())

        while not STOP.is_set():
            try:
                print "TCP Client waiting on gateway"
                ready = select.select([self.gateway_sock], [], [], 1)
            except:
                return
            if ready[0]:
                try:
                    print "TCP Client reading from gateway"
                    data = self.gateway_sock.recv(4096)
                except:
                    raise
            print "TCP Client received server list from Gateway"
            packet = Packet.decode(data)
            servers = packet.payload

            if len(servers) > 0:
                self.callback(servers[0])

class ConnectThread(Thread):
    def __init__(self, connect_sock, server):
        Thread.__init__(self)
        self.connect_sock = connect_sock
        self.server = server

    def run(self):
        while not STOP.is_set():
            try:
                self.connect_sock.connect(tuple(self.server))
            except socket.error:
                continue
            else:
                print "connected from --- success!"
                STOP.set()
        packet = Packet(CLIENT)
        packet.payload = "Requesting stuffs"
        self.connect_sock.send(packet.encode())
        data = self.connect_sock.recv(4096)
        print "Recieved response at client from connection: ", data

class LCPClientSocket(object):
    def __init__(self, gateway, tcp=True):
        self.tcp = tcp
        self.gateway = gateway
        self.gthread = None
        # Create 2 sockets
        self.gateway_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def bind(self, addr):
        self.connect_sock.bind( (addr[0], 0) )
        self.connect_recv_port = self.connect_sock.getsockname()[1]# Store this to communicate to gateway
        print "Client thread adding rcv_port", self.connect_recv_port

    def _trigger_connection(self, client):
        self.connect_thread = ConnectThread(self.connect_sock, client)
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

    def connect_and_send(self, MSG):
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
        self.connect_thread.join()
        sys.exit(-1)

def lambda_handler(event, context):
    sock = LCPClientSocket((event['ip'], int(event['port'])))
    sock.bind(('0.0.0.0', 0))
    sock.connect_and_send("Hello Lambda from Client")
