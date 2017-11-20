from __future__ import print_function

import json
import socket
import time

UDP_IP = "54.183.249.176"
UDP_PORT = 8888
MESSAGE = "lambda"

print('Loading function')


def lambda_handler(event, context):
    #print("Received event: " + json.dumps(event, indent=2))
    print("value1 = " + event['key1'])
    print("value2 = " + event['key2'])
    print("value3 = " + event['key3'])
    sock = socket.socket(socket.AF_INET, # Internet
                      socket.SOCK_DGRAM) # UDP
    while True:
        sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))
        data, addr = sock.recvfrom(4096)
        if data:
            break
        else:
            time.sleep(1)
    ip, port = eval(data)
    for i in xrange(10):
        sock.sendto("Hello Client, I'm the lambda!", (ip, port))
        time.sleep(0.5)
    data, addr = sock.recvfrom(4096)
    print("The client says" + str(data))
    print("This is awesome!!!!")
    return event['key1']  # Echo back the first key value
    #raise Exception('Something went wrong')
