import sys
import json
import base64

if __name__ == '__main__':
    #data = json.load(open(sys.argv[1], 'rb'))
    #log = data['LogResult']
    data = open(sys.argv[1], 'rb').readlines()
    log = data[0].split()[1]
    print base64.b64decode(log)
