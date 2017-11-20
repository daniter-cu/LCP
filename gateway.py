import socket
import sys
from structs import *



class Gateway(object):
    def __init__(self):
        self.clients = set()
        self.server = set()

    def run(self):
        UDP_IP = 0.0.0.0
        UDP_PORT = 8888
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

    def handle_client(packet, addr, sock):
        if addr not in self.clients:
            self.clients.add(addr)
        packet = Packet(GATEWAY)
        packet.add_payload(list(self.clients))
        for addr in self.servers:
            sock.sendto(packet, addr)
        return

    def handle_server(packet, addr, sock):
        pass

if __name__ == '__main__':
    gateway = Gatway()
    gateway.run()
