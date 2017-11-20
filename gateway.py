import socket
import sys
from structs import *

UDP_IP = "0.0.0.0"
UDP_PORT = 8888

class Gateway(object):
    def __init__(self):
        self.clients_g = set()
        self.servers_g = set()
        self.clients_p2p = set()
        self.servers_p2p = set()

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
        if addr not in self.clients_g:
            self.clients_g.add(addr)
            self.clients_p2p.add(packet.payload)

        # Tell the client about all the servers
        packet = Packet(GATEWAY)
        packet.add_payload(list(self.servers_p2p))
        sock.sendto(packet.encode(), addr)

        packet = Packet(GATEWAY)
        packet.add_payload(list(self.clients_p2p))
        for addr in self.servers_g:
            sock.sendto(packet.encode(), addr)
        return

    def handle_server(self, packet, addr, sock):
        print "Adding server", addr
        if addr not in self.servers_g:
            self.servers_g.add(addr)
            self.servers_p2p.add(packet.payload)

        # Tell the server about all the client
        packet = Packet(GATEWAY)
        packet.add_payload(list(self.clients_p2p))
        sock.sendto(packet.encode(), addr)

        packet = Packet(GATEWAY)
        packet.add_payload(list(self.servers_p2p))
        for addr in self.clients_g:
            sock.sendto(packet.encode(), addr)
        return

if __name__ == '__main__':
    gateway = Gateway()
    gateway.run()
