"""POX OpenFlow 1.0 demo controller for topology.py's fixed port layout.
Uses OF port status, not topology discovery; intended for this exact lab topology.
"""
from pox.core import core
import pox.openflow.libopenflow_01 as of
log=core.getLogger()
connections={};down=set();active=None
# physical link endpoints, based on topology.py link insertion order
links={'primary_a':((1,2),(2,1)),'primary_b':((2,2),(4,2)),
       'backup_a':((1,3),(3,1)),'backup_b':((3,2),(4,3))}
def healthy(label):
    return all(endpoint not in down for endpoint in links[label])
def add_pair(conn,p1,p2):
    for src,dst in ((p1,p2),(p2,p1)):
        m=of.ofp_flow_mod();m.priority=100;m.match=of.ofp_match(in_port=src)
        m.actions.append(of.ofp_action_output(port=dst));conn.send(m)
def refresh():
    global active
    if not all(x in connections for x in (1,2,3,4)):return
    if healthy('primary_a') and healthy('primary_b'):path='primary'
    elif healthy('backup_a') and healthy('backup_b'):path='backup'
    else:path='none'
    if path==active:return
    active=path;log.warning('ACTIVE PATH: %s',path)
    for conn in connections.values():
        m=of.ofp_flow_mod(command=of.OFPFC_DELETE);conn.send(m)
    if path=='none':return
    if path=='primary':rules={1:(1,2),2:(1,2),4:(1,2)}
    else:rules={1:(1,3),3:(1,2),4:(1,3)}
    for dpid,(a,b) in rules.items():add_pair(connections[dpid],a,b)
def connected(event):
    global active
    connections[event.dpid]=event.connection
    down.difference_update({p for p in down if p[0]==event.dpid})
    active=None;refresh()
def disconnected(event):
    global active
    connections.pop(event.dpid,None);active=None
    log.warning('Switch %s disconnected',event.dpid)
def port_status(event):
    global active
    port=event.ofp.desc.port_no
    key=(event.dpid,port)
    if port>of.OFPP_MAX:return
    is_down=(event.ofp.reason==of.OFPPR_DELETE or
             bool(event.ofp.desc.state & of.OFPPS_LINK_DOWN) or
             bool(event.ofp.desc.config & of.OFPPC_PORT_DOWN))
    if is_down:down.add(key)
    else:down.discard(key)
    active=None;refresh()
def launch():
    core.openflow.addListenerByName('ConnectionUp',connected)
    core.openflow.addListenerByName('ConnectionDown',disconnected)
    core.openflow.addListenerByName('PortStatus',port_status)
    log.warning('Reliable paths controller ready')
