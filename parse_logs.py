import sys
import json
import base64

if __name__ == '__main__':
    data = json.load(open(sys.argv[1], 'rb'))
    log = data['LogResult']
    print base64.b64decode(log)
