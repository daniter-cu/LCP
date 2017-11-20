import json
_types = ['CLIENT', 'SERVER', 'GATEWAY']
CLIENT = 'CLIENT'
SERVER = 'SERVER'
GATEWAY = 'GATEWAY'
TYPE = 'TYPE'
PAYLOAD = 'PAYLOAD'


class Packet(object):
    def __init__(self, _type):
        assert _type in _types
        self._type = _type
        self.payload = None

    def add_payload(self, payload):
        self.payload = payload

    def encode(self):
        try:
            json_packet = json.dumps({TYPE: self._type, PAYLOAD:self.payload})
        except ValueError:
            print "[FATAL] Failed to dump packet to json"
            return None
        return json_packet

    @staticmethod
    def decode(string_packet):
        try:
            json_packet = json.loads(string_packet)
        except ValueError:
            print "[FATAL] Failed to load packet from json"
            return None
        packet = Packet(json_packet[TYPE])
        packet.add_payload(json_packet[PAYLOAD])
        return packet
