import socket
from structs import *
from signal import signal, SIGTERM, SIGINT
import select
from threading import Thread, Event
import sys

STOP = Event()

class GatewayThread(Thread):
    def __init__(self, gateway, gateway_sock, recv_port, callback, MSG):
        Thread.__init__(self)
        self.gateway = gateway
        self.gateway_sock = gateway_sock
        self.recv_port = recv_port
        self.callback = callback
        self.MSG = MSG

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
                    data, _ = self.gateway_sock.recvfrom(4096)
                except:
                    raise
            print "TCP Client received server list from Gateway"
            packet = Packet.decode(data)
            servers = packet.payload

            if len(servers) > 0:
                # FIXME Here we only send packet to one client
                self.callback(servers[0], self.MSG)


class LCPClientSocket(object):
    def __init__(self, gateway, tcp=True):
        self.tcp = tcp
        self.gateway = gateway
        self.gthread = None

        # Create gateway socket
        self.gateway_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Create connection socket
        self.connect_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.connect_sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

    def bind(self, addr):
        self.connect_sock.bind( (addr[0], 0) )
        self.connect_recv_port = self.connect_sock.getsockname()[1]
        print "Client thread adding rcv_port", self.connect_recv_port

    def _trigger_connection(self, server, MSG):
        while not STOP.is_set():
            try:
                self.connect_sock.connect(tuple(server))
            except socket.error:
                continue
            else:
                print "LCP client connected"
                break
        print "Sending: " + MSG
        self.connect_sock.send(MSG)
        STOP.set()

    def connect_and_send(self, MSG):
        # Before we start listening we want to register with the gateway.
        # This should be done in a separate thread so it can continue to listen
        # for new events. Once that thread is kicked off we can start listening
        # on the recv_port.

        self.gateway_thread = GatewayThread(self.gateway, self.gateway_sock,
                                            self.connect_recv_port,
                                            self._trigger_connection,
                                            MSG)
        self.gateway_thread.start()
        while not STOP.is_set():
            continue

    def before_exit(self, *args):
        STOP.set()
        self.gateway_thread.join()
        sys.exit(-1)
