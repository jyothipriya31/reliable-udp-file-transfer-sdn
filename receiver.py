import argparse,json,os,socket,time
from protocol import CHUNK,pack,unpack,digest
p=argparse.ArgumentParser();p.add_argument('--bind',default='0.0.0.0');p.add_argument('--port',type=int,default=9000);p.add_argument('--outdir',default='received');p.add_argument('--drop-every',type=int,default=0,help='simulate dropping every Nth first-arrival data packet');p.add_argument('--lose-ack-once',action='store_true',help='simulate losing one ACK');a=p.parse_args()
os.makedirs(a.outdir,exist_ok=True)
s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM);s.bind((a.bind,a.port));s.settimeout(30)
print('Listening on',a.bind,a.port,flush=True)
expected=1;meta=None;f=None;path=None;peer_lock=None;duplicates=0;missing=0;dropped=set();ack_dropped=False;completed=False
try:
    while True:
        try:raw,peer=s.recvfrom(65535)
        except socket.timeout:
            if completed:break
            print('Receiver idle timeout');break
        try:kind,seq,payload=unpack(raw)
        except (ValueError,UnicodeDecodeError):continue
        if peer_lock is not None and peer!=peer_lock:continue
        if kind=='M' and seq==0:
            if meta is None:
                try:
                    proposed=json.loads(payload.decode()); name=os.path.basename(proposed['name']); size=int(proposed['size']);chunks=int(proposed['chunks']);sha=proposed['sha256']
                    if not name or name in ('.','..') or size<0 or chunks!=(size+CHUNK-1)//CHUNK or len(sha)!=64:continue
                    meta=proposed;peer_lock=peer;path=os.path.join(a.outdir,'received_'+name);f=open(path,'wb')
                except (ValueError,KeyError,TypeError,UnicodeDecodeError):continue
            s.sendto(pack('A',0),peer)
        elif kind=='D' and meta is not None and not completed:
            if seq==expected:
                if a.drop_every>0 and seq%a.drop_every==0 and seq not in dropped:
                    dropped.add(seq);print('Simulated loss:',seq,flush=True);continue
                remaining=meta['size']-(expected-1)*CHUNK
                if len(payload)!=min(CHUNK,remaining):continue
                f.write(payload);expected+=1
                if a.lose_ack_once and not ack_dropped:
                    ack_dropped=True
                    print('Simulated ACK loss:',seq,flush=True)
                else:
                    s.sendto(pack('A',seq),peer)
            elif seq<expected:
                duplicates+=1
                s.sendto(pack('A',seq),peer)
                print('Duplicate packet detected:',seq,'— ACK sent',flush=True)
            else:
                missing+=1;print('Out-of-order packet',seq,'expected',expected,flush=True)
        elif kind=='E' and meta is not None and seq==meta['chunks']+1:
            if expected==seq:
                if not completed:
                    f.flush();f.close();f=None
                    actual=digest(path);completed=actual==meta['sha256']
                    print(json.dumps({'integrity_ok':completed,'sha256':actual,'duplicates':duplicates,'out_of_order':missing,'saved_to':path}),flush=True)
                if completed:s.sendto(pack('A',seq),peer)
            else:print('Missing packets; expected',expected,flush=True)
finally:
    if f:f.close()
    s.close()
