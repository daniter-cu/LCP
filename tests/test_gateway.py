import sys
import os
import socket
path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(path +"/../")
import multiprocessing
import time

from gateway import Gateway, UDP_PORT
from structs import *

def gateway():
    print 'Gateway started'
    g = Gateway()
    g.run()
    return

def server():
    print 'Server running'
    sock = socket.socket(socket.AF_INET, # Internet
                          socket.SOCK_DGRAM)
    packet = Packet(SERVER)
    sock.sendto(packet.encode() , ('localhost', UDP_PORT))
    data, addr = sock.recvfrom(1024)
    print "At server", data
    p = Packet.decode(data)
    assert p._type == GATEWAY
    return

def client():
    print 'Client running'
    sock = socket.socket(socket.AF_INET, # Internet
                          socket.SOCK_DGRAM)
    packet = Packet(CLIENT)
    sock.sendto(packet.encode() , ('localhost', UDP_PORT))
    data, addr = sock.recvfrom(1024)
    print "At client", data
    p = Packet.decode(data)
    assert p._type == GATEWAY
    return

if __name__ == '__main__':
    jobs = []
    g = multiprocessing.Process(target=gateway)
    g.start()
    p = multiprocessing.Process(target=server)
    jobs.append(p)
    p.start()
    p = multiprocessing.Process(target=client)
    jobs.append(p)
    p.start()

    for j in jobs:
        j.join()
    time.sleep(0.5)
    g.terminate()
