import socket
import multiprocessing as mp
from structs import *
from signal import signal, SIGTERM


class LCPSocket(object):
    def __init__(self, gateway):
        self.gateway = gateway
        self.gthread = None
        # Create 2 sockets
        # gateway_sock -> Communicating with the gateway server
        # server_sock -> socket to get connections from client
        self.gateway_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
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

            packet = Packet(SERVER_PROBE)
            for client in clients:
                print "Sending a probe to client", client
                self.server_sock.sendto(packet.encode(), tuple(client))


    def listen(self, backlog=10):
        # Before we start listening we want to register with the gateway
        # This should be done in a separate thread so it can continue to listen
        # for new events
        # Once that thread is kicked off we can start listening on the recv_port
        if self.gthread is None:
            self.gthread = mp.Process(target=self.gateway_thread)
            self.gthread.start()
            signal(SIGTERM, self.before_exit)

        data, addr = self.server_sock.recvfrom(4096)
        print "Server request:", data
        packet = Packet(SERVER)
        packet.payload = "Returning some stuffs"
        self.server_sock.sendto(packet.encode(), addr)
        return data

def lambda_handler(event, context):
    sock = LCPSocket((event['ip'], int(event['port'])))
    sock.bind(('0.0.0.0', 0))
    sock.listen()
