import socket
from structs import *
from signal import signal, SIGTERM, SIGINT
import select
from threading import Thread, Event
import sys

STOP = Event()


class GatewayThread(Thread):
    def __init__(self, gateway, gateway_sock, recv_port, lcp):
        Thread.__init__(self)
        self.gateway = gateway
        self.gateway_sock = gateway_sock
        self.recv_port = recv_port
        self.lcp = lcp

    def run(self):
        '''
        # 1. Tell the gateway who you are
        # 2. Get all server from gateway
        '''
        print "TCP Server sending ID to Gateway"
        packet = Packet('CLIENT')
        packet.payload = ('localhost', self.recv_port)
        self.gateway_sock.connect(self.gateway)
        self.gateway_sock.send(packet.encode())

        # We only communicate with the gateway once
        while not STOP.is_set():
            try:
                print "TCP Client waiting on gateway"
                ready = select.select([self.gateway_sock], [], [], 1)
            except:
                return
            if ready[0]:
                try:
                    print "TCP Client reading from gateway"
                    data, _ = self.gateway_sock.recvfrom(4096)
                except:
                    raise
            print "TCP Client received server list from Gateway"
            packet = Packet.decode(data)
            servers = packet.payload

            if len(servers) > 0:
                self.lcp.add_server_list(servers)


class LCPClientSocket(object):
    def __init__(self, gateway, port=50000, tcp=True):
        self.gateway = gateway
        self.connect_port = port
        self.tcp = tcp
        self.gthread = None
        self.server_list = None
        self.socket_list = None

        # Lock until we get server list
        STOP.clear()

        # Create gateway socket
        self.gateway_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Get server list from gateway and initiate connection
        self.gateway_thread = GatewayThread(self.gateway, self.gateway_sock,
                                            self.connect_port, self)
        self.gateway_thread.start()

    def add_server_list(self, server_list):
        self.server_list = server_list
        self.socket_list = [None] * len(server_list)
        STOP.set()

    def get_socket(self, key):
        STOP.wait()

        index = abs(hash(key)) % len(self.server_list)
        if self.socket_list[index] is not None:
            return self.socket_list[index]

        print "Connecting for the first time"
        connect_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        connect_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        connect_sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        connect_sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        # Set SO_REUSEPORT
        connect_sock.setsockopt(socket.SOL_SOCKET, 15, 1)
        connect_sock.bind(('0.0.0.0', self.connect_port))
        connect_sock.connect(tuple(self.server_list[index]))
        self.socket_list[index] = connect_sock
        return connect_sock
