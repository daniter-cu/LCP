import socket
import threading
import sys
from structs import *
from signal import signal, SIGTERM, SIGINT
import select
import time

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
            try:
                ready = select.select([self.gateway_sock], [], [], 1)
            except:
                return
            if ready[0]:
                try:
                    data, _ = self.gateway_sock.recvfrom(4096)
                except:
                    return
                print data
                packet = Packet.decode(data)
                for addr in packet.payload:
                    self.server_list.add(tuple(addr))
                    print "Client adding server",  addr
        print "Exiting client gateway thread"

class LCPClientSocket(object):
    def __init__(self, gateway):
        self.gateway = gateway
        self.gthread = None
        self.server_list = set()
        self.t = None
        # Create 2 sockets
        # gateway_sock -> Communicating with the gateway server
        # server_sock -> socket to get connections from client
        self.gateway_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.client_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.gateway_sock.setblocking(0)

    def bind(self, addr):
        self.client_sock.bind(addr)
        self.recv_port = self.client_sock.getsockname()[1] # Store this to communicate to gateway
        print "THE PORT", self.recv_port

    def before_exit(self, *args):
        self.gateway_sock.close()
        self.t.join()
        sys.exit(-1)

    def send(self, msg):
        # Before we start listening we want to register with the gateway
        # This should be done in a separate thread so it can continue to listen
        # for new events
        # Once that thread is kicked off we can start listening on the recv_port
        if self.t is None:
            self.t = GatewayThread(self.server_list, self.gateway, self.gateway_sock, self.recv_port)
            self.t.start()
            signal(SIGTERM, self.before_exit)
            signal(SIGINT, self.before_exit)

        packet = Packet(CLIENT)
        packet.payload = msg
        while len(self.server_list) == 0:
            time.sleep(.25)
            if not self.t.is_alive():
                return
        target_addr = next(iter(self.server_list))
        print target_addr
        self.client_sock.sendto(packet.encode(), target_addr)
        while True:
            print "Request sent, waiting for response from server"
            data, addr = self.client_sock.recvfrom(4095)
            p = Packet.decode(data)
            if p._type == SERVER_PROBE:
                continue
            print "Client received response", data
            break
        return data

def lambda_handler(event, context):
    sock = LCPClientSocket((event['ip'], int(event['port'])))
    sock.bind(('0.0.0.0', 0))
    try:
        sock.send("Hello Lambda!")
    except:
        print sys.exc_info()
        sock.before_exit(None)
    sock.before_exit(None)
    return

if __name__ == '__main__':
    sock = LCPClientSocket((sys.argv[1], 8888))
    sock.bind(('0.0.0.0', 0))
    try:
        sock.send("Hello Lambda!")
    except:
        print sys.exc_info()
        sock.before_exit(None)
    time.sleep(25)
    sock.send("Hello Lambda!")
    sock.before_exit(None)
