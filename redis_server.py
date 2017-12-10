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
    def __init__(self, gateway, gateway_sock, connect_port, callback):
        Thread.__init__(self)
        self.gateway = gateway
        self.gateway_sock = gateway_sock
        self.connect_port = connect_port
        self.callback = callback
        self.threads = []
        self.clients_connected = []

    def run(self):
        '''
        # 1. Tell the gateway who you are
        # 2. Get all clients from gateway
        # 3. send all clients a packet from connect_port
        # 4. monitor gateway for new events
        '''
        #print "TCP Server sending ID to Gateway"
        packet = Packet('SERVER')
        packet.payload = ('localhost', self.connect_port)
        self.gateway_sock.connect(self.gateway)
        self.gateway_sock.send(packet.encode())

        while not STOP.is_set():
            try:
                ready = select.select([self.gateway_sock], [], [], 1)
            except:
                raise
            if ready[0]:
                try:
                    #print "TCP Server reading from gateway"
                    data = self.gateway_sock.recv(4096)
                    if len(data) == 0:
                        continue
                    while "SPECIAL_END" not in data:
                        data += self.gateway_sock.recv(4096)
                except:
                    return
                else:
                    #print "TCP Server received clients list from Gateway"
                    #print "###################"
                    #print data
                    #print "###################"
                    packet = Packet.decode(data)
                    clients = packet.payload

                    for client in clients:
                        if client not in self.clients_connected:
                            #print "handling client " + str(client[0])
                            connect_thread = ConnectThread(client, self.connect_port)
                            connect_thread.start()
                            self.threads.append(connect_thread)
                            self.clients_connected.append(client)

        while len(self.threads) > 0:
            for thread in self.threads:
                try:
                    thread.join(1)
                except TimeoutError:
                    continue
                if not thread.is_alive():
                    self.threads.remove(thread)


class ConnectThread(Thread):
    def __init__(self, client, connect_port):
        Thread.__init__(self)
        self.client = client
        self.connect_port = connect_port

    def run(self):
        flag = 0
        while not flag:
            try:
                connect_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                connect_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                #connect_sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                #connect_sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
                #connect_sock.setsockopt(socket.SOL_SOCKET, 15, 1)
                connect_sock.bind(('0.0.0.0', self.connect_port))
                #print "Trying to establish connection from Serveri at port: " + str(self.connect_port)
                #print tuple(self.client)
                connect_sock.connect(tuple(self.client))
                #print "Connection at server should succeed"
            except OSError as e:
                print e
                return
            except socket.error as e:
                print e
                print "[BAD] Some kind of socket error on Server"
                return
            else:
                #print "connected from --- success!"
                flag = 1
        #print "Got connected on server, trying ot read data"
	print "Connected to " + str(self.client[1]) 

        redis_sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        #print ">>> trying to connect to redis server"
        server_address = '/tmp/redis.sock'
        try:
            redis_sock.connect(server_address)
        except socket.error, msg:
            print >>sys.stderr, msg
            sys.exit(1)
        #print ">>> connected to redis server"

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
	    data = connect_sock.recv(1048576)
            if len(data) == 0:
                return
            rem = self.parse_data(data)
            while rem > 0:
                temp_data = connect_sock.recv(1048576)
                data += temp_data
                rem -= len(temp_data)
	    redis_sock.sendall(data)
	    response = redis_sock.recv(1048576)
            rem = self.parse_response(data[8] == 'G', response)
            while rem > 0:
	        temp_response = redis_sock.recv(1048576)
	        response += temp_response
                rem -= len(temp_response)
            connect_sock.send(response)

    def parse_response(self, is_get, response):
        if not is_get:
            return 0
        value_length_end = response.find('\r\n')
        value_length = int(response[1:value_length_end])
        return value_length_end + value_length + 4 - len(response)

    def parse_data(self, data):
        if data[8] == 'G':
            return 0
        first_r_n = 14 + data[14:].find('\r\n')
        second_r_n = first_r_n + 1 + data[first_r_n + 1:].find('\r\n')
        value_size_start = second_r_n + 3
        value_size_end = value_size_start + data[value_size_start:].find('\r\n')
        value_size = int(data[value_size_start:value_size_end])
        return value_size_end + 4 + value_size - len(data)


class LCPSocket(object):
    def __init__(self, gateway, connect_port, tcp=True):
        self.tcp = tcp
        self.gateway = gateway
        self.gthread = None
        self.gateway_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect_port = connect_port
        #print "Server thread binding to connect_port", self.connect_port

    def _trigger_connection(self, client):
        self.connect_thread = ConnectThread(client, self.connect_port)
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
        # Once that thread is kicked off we can start listening on the connect_port

        self.gateway_thread = GatewayThread(self.gateway, self.gateway_sock, self.connect_port, self._trigger_connection)
        self.gateway_thread.start()
        signal(SIGTERM, self.before_exit)
        signal(SIGINT, self.before_exit)

        while True:
            time.sleep(1)

    def before_exit(self, *args):
        STOP.set()
        self.gateway_thread.join()
        sys.exit(-1)

def lambda_handler(event, context):
    subprocess.Popen(['./redis-server', './redis.conf'])
    sock = LCPSocket((event['ip'], int(event['port'])), int(event['connect_port']))
    sock.listen()
