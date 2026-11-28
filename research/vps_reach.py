"""Logs every 5 min whether each VPS remote-desktop port (from accounts.json notes) accepts a TCP connection. No login, no data sent.
Output: data/derived/vps/reach.csv (time, VPS letter, ok, ms). Usage: py -3.12 research/vps_reach.py [hours]"""
import json, socket, time, sys, datetime as dt
H = float(sys.argv[1]) if len(sys.argv) > 1 else 24
eps = []
for a in json.load(open("accounts.json")):
    n = a.get("note", "")
    if ":" in n and n.count(".") == 3 and n not in eps: eps.append(n)
end = time.time() + H * 3600
while time.time() < end:
    for i, n in enumerate(eps):
        h, p = n.split(":"); t = time.time()
        try: s = socket.create_connection((h, int(p)), timeout=8); s.close(); ok, ms = 1, int((time.time() - t) * 1000)
        except Exception: ok, ms = 0, -1
        with open("data/derived/vps/reach.csv", "a") as f: f.write(f"{dt.datetime.now():%Y-%m-%d %H:%M},{chr(65 + i)},{ok},{ms}\n")
    time.sleep(300)
