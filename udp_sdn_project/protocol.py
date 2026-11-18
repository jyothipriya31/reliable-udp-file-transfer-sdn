import hashlib, json, struct
CHUNK=1000
HEADER=struct.Struct('!cI')
def pack(kind, seq, payload=b''):
    return HEADER.pack(kind.encode(),seq)+payload
def unpack(data):
    if len(data)<HEADER.size: raise ValueError('short packet')
    kind,seq=HEADER.unpack(data[:HEADER.size]); return kind.decode(),seq,data[HEADER.size:]
def digest(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for block in iter(lambda:f.read(65536),b''):h.update(block)
    return h.hexdigest()
