import socket
import json
import hashlib
import math
from protocol import CHUNK, pack

with open("sample.txt", "rb") as f:
    data = f.read()

metadata = {
    "name": "out_of_order_demo.txt",
    "size": len(data),
    "chunks": math.ceil(len(data) / CHUNK),
    "sha256": hashlib.sha256(data).hexdigest()
}

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.settimeout(3)
target = ("10.0.0.2", 9001)

sock.sendto(pack("M", 0, json.dumps(metadata).encode()), target)

try:
    sock.recvfrom(65535)
    print("Metadata ACK received")
    sock.sendto(pack("D", 2, data[CHUNK:2*CHUNK]), target)
    print("Deliberately sent data packet 2 before packet 1")
except socket.timeout:
    print("No metadata ACK received. Check the receiver.")

sock.close()
