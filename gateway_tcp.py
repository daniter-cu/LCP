import socket
import sys
from structs import *
from threading import Thread, Event, Lock
import select
from signal import signal, SIGTERM, SIGINT
import time


UDP_IP = "0.0.0.0"
UDP_PORT = 8888

STOP = Event()

class ConnectionThread(Thread):
    def __init__(self, gateway, conn, addr):
        Thread.__init__(self)
        self.conn = conn
        self.gateway = gateway
        self.addr = addr
        self.UPDATE_SERVERS = Event()
        self.UPDATE_CLIENTS = Event()
        self._type = None

    def run(self):
        while not STOP.is_set():
            readable, _, _ = select.select([self.conn], [], [], 1)
            if readable:
                data = self.conn.recv(4096)
                if len(data) == 0:
                    time.sleep(0.1)
                    continue
                packet = Packet.decode(data)
                if packet is None:
                    continue
                if packet._type == CLIENT:
                    self._type = CLIENT
                    self.handle_client(packet)
                    with self.gateway.thread_lock:
                        for t in self.gateway.threads:
                            t.UPDATE_SERVERS.set()
                if packet._type == SERVER:
                    self._type = SERVER
                    self.handle_server(packet)
                    with self.gateway.thread_lock:
                        for t in self.gateway.threads:
                            t.UPDATE_CLIENTS.set()
            if self.UPDATE_SERVERS.is_set() and self._type == SERVER:
                self.update_servers()
                self.UPDATE_SERVERS.clear()
            if self.UPDATE_CLIENTS.is_set() and self._type == CLIENT:
                self.update_clients()
                self.UPDATE_CLIENTS.clear()

    def update_clients(self):
        packet = Packet(GATEWAY)
        packet.add_payload(list(self.gateway.servers_p2p))
        self.conn.send(packet.encode())
        print "GATEWAY: Servers sent to clients"

    def update_servers(self):
        packet = Packet(GATEWAY)
        packet.add_payload(list(self.gateway.clients_p2p))
        self.conn.send(packet.encode())
        print "GATEWAY: Clients sent to servers"

    def handle_client(self, packet):
        print "Adding client", self.addr
        with self.gateway.list_lock:
            self.gateway.clients_p2p.add((self.addr[0], packet.payload[1]))

        # Tell the client about all the servers
        packet = Packet(GATEWAY)
        packet.add_payload(list(self.gateway.servers_p2p))
        self.conn.send(packet.encode())
        return

    def handle_server(self, packet):
        print "Adding server", self.addr
        with self.gateway.list_lock:
            self.gateway.servers_p2p.add((self.addr[0], packet.payload[1]))

        # Tell the server about all the client
        packet = Packet(GATEWAY)
        packet.add_payload(list(self.gateway.clients_p2p))
        self.conn.send(packet.encode())
        return

class Gateway(object):
    def __init__(self):
        self.clients_p2p = set()
        self.servers_p2p = set()
        self.list_lock = Lock()
        self.threads = []
        self.thread_lock = Lock()

    def run(self):
        print "Gateway started..."
        sock = socket.socket(socket.AF_INET, # Internet
                              socket.SOCK_STREAM) # UDP
        sock.bind((UDP_IP, UDP_PORT))
        sock.listen(5)

        signal(SIGTERM, self.before_exit)
        signal(SIGINT, self.before_exit)

        while True:
            conn, addr = sock.accept()
            t = ConnectionThread( self, conn, addr )
            with self.thread_lock:
                self.threads.append(t)
            t.start()

    def before_exit(self, *args):
        STOP.set()
        for t in self.threads:
            t.join()
        sys.exit(-1)


if __name__ == '__main__':
    gateway = Gateway()
    gateway.run()
