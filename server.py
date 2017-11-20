import socket

class LCPSocket(object):
    def __init__(self, gateway, udp=False):
        self.udp = udp
        self.gateway = gateway
        if udp:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        else:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def bind(self, addr):
        self.sock.bind(addr)
        self.sock.settimeout(10)
        self.sock.connect(self.gateway)
        self.sock.settimeout(None)

    def listen(self, backlog=10):
        self.sock.listen(backlog)














if __name__ == '__main__':
    sock = LCPSocket(('127.0.0.1', 5005))
    sock.bind(('127.0.0.1', 8888))
    sock.listen()
