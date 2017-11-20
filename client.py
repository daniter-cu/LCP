import socket
import threading
from structs import *
from signal import signal, SIGTERM

class GatewayThread(threading.Thread):
    def __init__(self, server_list, gateway, gateway_sock, recv_port):
        threading.Thread.__init__(self)
        self.server_list = server_list
        self.gateway_sock = gateway_sock
        self.recv_port = recv_port
        self.gateway = gateway

    def run(self):
        print "Starting client gateway thread"
        packet = Packet(CLIENT)
        packet.payload = ('localhost', self.recv_port)
        self.gateway_sock.sendto(packet.encode(), self.gateway)

        while True:
            data, _ = self.gateway_sock.recvfrom(4096)
            packet = Packet.decode(data)
            for addr in packet.payload:
                self.server_list.add(tuple(addr))
        print "Exiting client gateway thread"

class LCPClientSocket(object):
    def __init__(self, gateway):
        self.gateway = gateway
        self.gthread = None
        self.server_list = set()
        # Create 2 sockets
        # gateway_sock -> Communicating with the gateway server
        # server_sock -> socket to get connections from client
        self.gateway_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.client_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def bind(self, addr):
        self.client_sock.bind(addr)
        self.recv_port = addr[1] # Store this to communicate to gateway

    def send(self, msg):
        # Before we start listening we want to register with the gateway
        # This should be done in a separate thread so it can continue to listen
        # for new events
        # Once that thread is kicked off we can start listening on the recv_port
        t = GatewayThread(self.server_list, self.gateway, self.gateway_sock, self.recv_port)
        t.start()

        packet = Packet(CLIENT)
        packet.payload = msg
        while len(self.server_list) == 0:
            pass
        self.client_sock.sendto(packet.encode(), next(iter(self.server_list)))
        while True:
            data, addr = self.client_sock.recvfrom(4095)
            p = Packet.decode(data)
            if p._type == SERVER_PROBE:
                continue
            print "Client received response", data
        return data

if __name__ == '__main__':
    sock = LCPSocket(('127.0.0.1', 8888))
    sock.bind(('127.0.0.1', 5005))
    sock.listen()
