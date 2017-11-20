import socket
import sys
from structs import *

UDP_IP = "0.0.0.0"
UDP_PORT = 8888

class Gateway(object):
    def __init__(self):
        self.clients = set()
        self.servers = set()

    def run(self):
        sock = socket.socket(socket.AF_INET, # Internet
                              socket.SOCK_DGRAM) # UDP
        sock.bind((UDP_IP, UDP_PORT))

        while True:
            data, addr = sock.recvfrom(4096) # buffer size is 1024 bytes
            packet = Packet.decode(data)
            if packet is None:
                continue
            if packet._type == CLIENT:
                self.handle_client(packet, addr, sock)
            if packet._type == SERVER:
                self.handle_server(packet, addr, sock)

    def handle_client(self, packet, addr, sock):
        print "Adding client", addr
        if addr not in self.clients:
            self.clients.add(addr)

        # Tell the client about all the servers
        packet = Packet(GATEWAY)
        packet.add_payload(list(self.servers))
        sock.sendto(packet.encode(), addr)

        packet = Packet(GATEWAY)
        packet.add_payload(list(self.clients))
        for addr in self.servers:
            sock.sendto(packet.encode(), addr)
        return

    def handle_server(self, packet, addr, sock):
        print "Adding server", addr
        if addr not in self.servers:
            self.servers.add(addr)

        # Tell the server about all the client
        packet = Packet(GATEWAY)
        packet.add_payload(list(self.clients))
        sock.sendto(packet.encode(), addr)

        packet = Packet(GATEWAY)
        packet.add_payload(list(self.servers))
        for addr in self.clients:
            sock.sendto(packet.encode(), addr)
        return

if __name__ == '__main__':
    gateway = Gateway()
    gateway.run()
