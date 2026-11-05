import sys, time
import paho.mqtt.client as m

# Usage: test_clients.py host [clients] [timeout]
H = sys.argv[1]
N = int(sys.argv[2]) if len(sys.argv) > 2 else 10
T = float(sys.argv[3]) if len(sys.argv) > 3 else 10

cs = []
for i in range(N):
    c = m.Client(m.CallbackAPIVersion.VERSION2, client_id=f'k{i}')
    c.rc = None
    c.on_connect = lambda cc, u, f, rc, p: setattr(cc, 'rc', rc)
    t = time.time()
    try:
        c.connect(H, 1883, 30)
    except Exception as e:
        print(f'client {i}: TCP failed: {e}')
        continue
    c.loop_start()
    while c.rc is None and time.time() - t < T:
        time.sleep(.02)
    print(f'client {i}: {c.rc} after {time.time() - t:.2f} s')
    cs.append(c)

ok = sum(c.rc is not None and not c.rc.is_failure for c in cs)
print('connected', ok, '/', N)
for c in cs:
    c.loop_stop()
    c.disconnect()
