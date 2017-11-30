import sys
import os
import socket
path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(path +"/../")
import multiprocessing
import time

from gateway import Gateway, UDP_PORT
from structs import *
from server_tcp import *
from client_tcp import *

GATEWAY_ADDR = ('localhost', UDP_PORT)

def gateway():
    print 'Gateway started'
    g = Gateway()
    g.run()
    return

def server():
    print 'Server running'
    sock = LCPSocket(GATEWAY_ADDR)
    sock.bind(('localhost', 5005))
    sock.listen()
    return

def client():
    print 'Client running'
    sock = LCPClientSocket(GATEWAY_ADDR)
    sock.bind(('localhost', 5010))
    sock.connect_and_send("Request some stuffs")
    return

if __name__ == '__main__':
    jobs = []
    g = multiprocessing.Process(target=gateway)
    g.start()

    p = multiprocessing.Process(target=server)
    jobs.append(p)
    p.start()

    time.sleep(.5)
    p = multiprocessing.Process(target=client)
    jobs.append(p)
    p.start()

    for j in jobs:
        j.join(2)
        j.terminate()

    time.sleep(0.5)
    g.terminate()
