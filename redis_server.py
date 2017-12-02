import subprocess
import json

import socket
from structs import *
from signal import signal, SIGTERM, SIGINT
import time
import select
from threading import Thread, Event
import sys

STOP = Event()

class GatewayThread(Thread):
    def __init__(self, gateway, gateway_sock, recv_port, callback):
        Thread.__init__(self)
        self.gateway = gateway
        self.gateway_sock = gateway_sock
        self.recv_port = recv_port
        self.callback = callback

    def run(self):
        '''
        # 1. Tell the gateway who you are
        # 2. Get all clients from gateway
        # 3. send all clients a packet from recv_port
        # 4. monitor gateway for new events
        '''
        print "TCP Server sending ID to Gateway"
        packet = Packet('SERVER')
        packet.payload = ('localhost', self.recv_port)
        self.gateway_sock.connect(self.gateway)
        self.gateway_sock.send(packet.encode())

        while not STOP.is_set():
            try:
                print "TCP Server waiting on gateway"
                ready = select.select([self.gateway_sock], [], [], 1)
            except:
                raise
            if ready[0]:
                try:
                    print "TCP Server reading from gateway"
                    data = self.gateway_sock.recv(4096)
                except:
                    return
                else:
                    print "TCP Server received clients list from Gateway"
                    print "###################"
                    print data
                    print "###################"
                    packet = Packet.decode(data)
                    clients = packet.payload

                    for client in clients:
                        self.callback(client)


class ConnectThread(Thread):
    def __init__(self, connect_sock, client):
        Thread.__init__(self)
        self.connect_sock = connect_sock
        self.client = client

    def run(self):
        while not STOP.is_set():
            try:
                print "Trying to establish connection from Server"
                print tuple(self.client)
                self.connect_sock.connect(tuple(self.client))
                print "Connection at server should succeed"
            except socket.error as e:
                print e
                print "[BAD] Some kind of socket error on Server"
                return
            else:
                print "connected from --- success!"
                STOP.set()
        print "Got connected on server, trying ot read data"


        redis_sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        print ">>> trying to connect to redis server"
        server_address = '/tmp/redis.sock'
        try:
            redis_sock.connect(server_address)
        except socket.error, msg:
            print >>sys.stderr, msg
            sys.exit(1)
        print ">>> connected to redis server"

	''' 	
	# testing connection with redis server
	redis_sock.sendall('*1\r\n$4\r\nping\r\n')
	data = redis_sock.recv(4096)
	print "ping response: " + data
	redis_sock.sendall('*3\r\n$3\r\nSET\r\n$5\r\nmykey\r\n$7\r\nmyvalue\r\n')
	data = redis_sock.recv(4096)
	print "set response: " + data
	redis_sock.sendall('*2\r\n$3\r\nGET\r\n$5\r\nmykey\r\n')
	data = redis_sock.recv(4096)
	print "get response: " + data

        packet = Packet(SERVER)
        packet.payload = "Returning some stuffs"
	self.connect_sock.send(packet.encode())	
	'''
	STOP.clear()
        while not STOP.is_set():
	    data = self.connect_sock.recv(4096)
            print "Recieved client request at server from accepted connection: ", data	
	    d = json.loads(data)
	    #print "request from client: " + d["PAYLOAD"]
	    redis_sock.sendall(d["PAYLOAD"])
	    response = redis_sock.recv(4096)
	    packet = Packet(SERVER)
 	    packet.payload = response
	    print "response from redis server: " + response
            self.connect_sock.send(packet.encode())

class LCPSocket(object):
    def __init__(self, gateway, tcp=True):
        self.tcp = tcp
        self.gateway = gateway
        self.gthread = None
        # Create 2 sockets
        self.gateway_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


    def bind(self, addr):
        self.connect_sock.bind( (addr[0], 0) )
        self.connect_recv_port = self.connect_sock.getsockname()[1]# Store this to communicate to gateway
        print "Server thread adding rcv_port", self.connect_recv_port

    def _trigger_connection(self, client):
        self.connect_thread = ConnectThread(self.connect_sock, client)
        self.connect_thread.start()
        threads = [ self.connect_thread ] # self.accept_thread,
        while len(threads) > 0:
            for thread in threads:
                try:
                    thread.join(1)
                except TimeoutError:
                    continue
                if not thread.is_alive():
                    threads.remove(thread)

    def listen(self, backlog=5):
        # Before we start listening we want to register with the gateway
        # This should be done in a separate thread so it can continue to listen
        # for new events
        # Once that thread is kicked off we can start listening on the recv_port

        self.gateway_thread = GatewayThread(self.gateway, self.gateway_sock, self.connect_recv_port, self._trigger_connection)
        self.gateway_thread.start()
        signal(SIGTERM, self.before_exit)
        signal(SIGINT, self.before_exit)

        while True:
            time.sleep(1)

    def before_exit(self, *args):
        STOP.set()
        self.gateway_thread.join()
        #self.accept_thread.join()
        self.connect_thread.join()
        sys.exit(-1)

def lambda_handler(event, context):
    subprocess.Popen(['./redis-server', './redis.conf'])
    '''
    time.sleep(5)
    redis_sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    print ">>> trying to connect to redis server"
    server_address = '/tmp/redis.sock'
    try:
        redis_sock.connect(server_address)
    except socket.error, msg:
        print >>sys.stderr, msg
        sys.exit(1)
    print ">>> connected to redis server"
    '''
    sock = LCPSocket((event['ip'], int(event['port'])))
    sock.bind(('0.0.0.0', 0))
    sock.listen()
