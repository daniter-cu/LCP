import socket
import multiprocessing as mp
from structs import *
from signal import signal, SIGTERM
import time


class LCPSocket(object):
    def __init__(self, gateway, tcp=False):
        self.tcp = tcp
        self.gateway = gateway
        self.gthread = None
        # Create 2 sockets
        # gateway_sock -> Communicating with the gateway server
        # server_sock -> socket to get connections from client
        self.gateway_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        if tcp:
            self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        else:
            self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def bind(self, addr):
        self.server_sock.bind(addr)
        self.recv_port = self.server_sock.getsockname()[1]# Store this to communicate to gateway
        print "Server thread adding rcv_port", self.recv_port


    def before_exit(self, *args):
        if self.gthread is not None:
            self.gthread.terminate()

    def gateway_thread(self):
        '''
        # 1. Tell the gateway who you are
        # 2. Get all clients from gateway
        # 3. send all clients a packet from recv_port
        # 4. monitor gateway for new events
        '''
        packet = Packet('SERVER')
        packet.payload = ('localhost', self.recv_port)
        self.gateway_sock.sendto(packet.encode(), self.gateway)

        while True:
            data, _ = self.gateway_sock.recvfrom(4096)
            packet = Packet.decode(data)
            clients = packet.payload

            if self.tcp:
                for client in clients:
                    print "Sending a probe to client", client
                    tmp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    tmp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    tmp_socket.bind(('0.0.0.0', self.recv_port))
                    tmp_socket.settimeout(1)
                    tmp_socket.connect(tuple(client))
                    tmp_socket.settimeout(None)
            else:
                packet = Packet(SERVER_PROBE)
                for client in clients:
                    print "Sending a probe to client", client
                    self.server_sock.sendto(packet.encode(), tuple(client))


    def listen(self, backlog=5):
        # Before we start listening we want to register with the gateway
        # This should be done in a separate thread so it can continue to listen
        # for new events
        # Once that thread is kicked off we can start listening on the recv_port
        if self.gthread is None:
            self.gthread = mp.Process(target=self.gateway_thread)
            self.gthread.start()
            signal(SIGTERM, self.before_exit)

        if self.tcp:
            time.sleep(1)
            self.server_sock.listen(1)
            conn, addr = self.server_sock.accept()
            data = conn.recv(4096)
            print "Server request:", data
            packet = Packet(SERVER)
            packet.payload = "Returning some stuffs"
            self.server_sock.send(packet.encode())
            return data
        else:
            data, addr = self.server_sock.recvfrom(4096)
            print "Server request:", data
            packet = Packet(SERVER)
            packet.payload = "Returning some stuffs"
            self.server_sock.sendto(packet.encode(), addr)
            return data

def lambda_handler(event, context):
    sock = LCPSocket((event['ip'], int(event['port'])))
    sock.bind(('0.0.0.0', 0))
    while True:
        sock.listen()
