import sys
import os
import socket
path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(path +"/../")
import multiprocessing
import time

from gateway import Gateway, UDP_PORT
from structs import *
from server import *

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
    sock = socket.socket(socket.AF_INET, # Internet
                          socket.SOCK_DGRAM)
    packet = Packet(CLIENT)
    packet.payload = ('localhost', 5545)
    sock.sendto(packet.encode() , GATEWAY_ADDR)
    while True:
        data, addr = sock.recvfrom(1024)
        print "At client", data
        p = Packet.decode(data)

        if p._type == GATEWAY:
            packet = Packet(CLIENT)
            sock.sendto(packet.encode(), tuple(p.payload[0]))

        if p._type == SERVER:
            break
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
        j.join(1)
        j.terminate()

    time.sleep(0.5)
    g.terminate()
