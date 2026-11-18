import argparse, json, os, socket, time
from protocol import CHUNK,pack,unpack,digest
p=argparse.ArgumentParser();p.add_argument('file');p.add_argument('--host',default='10.0.0.2');p.add_argument('--port',type=int,default=9000);p.add_argument('--timeout',type=float,default=.5);p.add_argument('--retries',type=int,default=100);a=p.parse_args()
size=os.path.getsize(a.file); count=(size+CHUNK-1)//CHUNK
meta=json.dumps({'name':os.path.basename(a.file),'size':size,'chunks':count,'sha256':digest(a.file)}).encode()
s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM);s.settimeout(a.timeout)
retransmissions=0; start=time.monotonic()
def send_wait(kind,seq,payload=b''):
    global retransmissions
    for attempt in range(a.retries+1):
        s.sendto(pack(kind,seq,payload),(a.host,a.port))
        if attempt: retransmissions+=1
        deadline=time.monotonic()+a.timeout
        while True:
            remaining=deadline-time.monotonic()
            if remaining<=0:break
            s.settimeout(remaining)
            try: data,peer=s.recvfrom(4096)
            except socket.timeout:break
            try: k,n,_=unpack(data)
            except (ValueError,UnicodeDecodeError):continue
            if peer==(a.host,a.port) and k=='A' and n==seq:return
    raise TimeoutError(f'No ACK for {kind} sequence {seq}')
try:
    send_wait('M',0,meta)
    with open(a.file,'rb') as f:
        for seq in range(1,count+1):
            send_wait('D',seq,f.read(CHUNK))
            if seq%100==0:print('ACKed chunks:',seq,'/',count,flush=True)
    send_wait('E',count+1)
    elapsed=time.monotonic()-start
    print(json.dumps({'status':'sender_complete','bytes':size,'seconds':round(elapsed,3),'retransmissions':retransmissions,'throughput_kib_s':round(size/1024/max(elapsed,0.0001),2)}))
finally:s.close()
