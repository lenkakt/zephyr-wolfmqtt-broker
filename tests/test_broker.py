import sys,time,threading
import paho.mqtt.client as m
H,P=(sys.argv[1] if len(sys.argv)>1 else '127.0.0.1'),1883
def cl(i,**k):
    c=m.Client(m.CallbackAPIVersion.VERSION2,client_id=i,**k); c.rx=[]; c.rc=None
    c.on_message=lambda cc,u,msg:cc.rx.append((msg.topic,msg.payload.decode(),msg.qos,msg.retain))
    c.on_connect=lambda cc,u,f,rc,p:setattr(cc,'rc',rc)
    return c
def up(c):
    c.connect(H,P,30); c.loop_start(); t=time.time()
    while c.rc is None and time.time()-t<3: time.sleep(.02)
    return c.rc is not None and not c.rc.is_failure
R=[]
def ck(n,ok,x=''): R.append(ok); print(('PASS' if ok else 'FAIL'),n,x)
a=cl('a'); b=cl('b'); ck('connect',up(a) and up(b))
a.subscribe('greenhouse/#',1); time.sleep(.3)
b.publish('greenhouse/temp','21.5',qos=0); b.publish('greenhouse/hum','40',qos=1).wait_for_publish(3); b.publish('other/x','no',qos=0); time.sleep(.5)
ck('wildcard, QoS 0/1',len(a.rx)==2 and {x[0] for x in a.rx}=={'greenhouse/temp','greenhouse/hum'},a.rx)
i=b.publish('t/q2','two',qos=2); i.wait_for_publish(3); ck('QoS 2 publish',i.is_published())
b.publish('ret/x','kept',qos=1,retain=True).wait_for_publish(3); time.sleep(.2)
c=cl('c'); up(c); c.subscribe('ret/+',1); time.sleep(.5); ck('retained',any(x[1]=='kept' and x[3] for x in c.rx),c.rx)
w=cl('w'); w.will_set('will/w','gone',qos=1); up(w); time.sleep(.1)
a.subscribe('will/#',1); time.sleep(.3); w.loop_stop(); w._sock.close(); time.sleep(1.5); ck('last will',any(x[0]=='will/w' for x in a.rx),a.rx[-1:])
for x in (a,b,c):
    x.loop_stop(); x.disconnect()
time.sleep(.5)
v5=m.Client(m.CallbackAPIVersion.VERSION2,client_id='v5',protocol=m.MQTTv5); v5.rc=None
v5.on_connect=lambda cc,u,f,rc,p:setattr(cc,'rc',rc); v5.connect(H,P,30); v5.loop_start(); time.sleep(.6); ck('MQTT 5 connect',v5.rc is not None and not v5.rc.is_failure,v5.rc); v5.loop_stop(); v5.disconnect(); time.sleep(.5)
cs=[cl(f'n{i}') for i in range(10)]; ok=sum(up(x) for x in cs); ck('10 clients',ok==10,ok)
for x in cs: x.subscribe('all/#',1)
time.sleep(.5); cs[0].publish('all/m','hi',qos=1); time.sleep(1); n=sum(len(x.rx)>0 for x in cs); ck('fan-out to 10',n==10,n)
ex=cl('extra'); 
try:
    e=up(ex); time.sleep(1); print('INFO 11th client connected:',e,ex.rc,'still',ex.is_connected())
except Exception as ee: print('INFO 11th refused',ee)
ex.loop_stop()
for x in cs: x.loop_stop()
t=time.time();N=0
p=cs[1]
print('summary',sum(R),'/',len(R))
