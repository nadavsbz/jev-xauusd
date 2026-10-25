"""Capture the JSON a copy-trading rating page loads, through a headless Edge and the Chrome DevTools
Protocol (the rating API refuses plain HTTP clients). Scrolls to load more pages.
Usage: python research/copy/cdp_capture.py URL MATCH OUT_JSON [SCROLLS]
Writes a list of {url, body} for every response whose URL contains MATCH."""
import json, subprocess, sys, time, urllib.request, os, tempfile
import websocket

EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"


def main():
    url, match, out = sys.argv[1], sys.argv[2], sys.argv[3]
    scrolls = int(sys.argv[4]) if len(sys.argv) > 4 else 10
    prof = tempfile.mkdtemp(prefix="cdp_")
    p = subprocess.Popen([EDGE, "--headless=new", "--disable-gpu", "--remote-debugging-port=9333", "--remote-allow-origins=*", f"--user-data-dir={prof}",
                          "--window-size=1600,4000", "about:blank"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        for _ in range(40):
            try:
                tabs = json.load(urllib.request.urlopen("http://localhost:9333/json")); break
            except Exception:
                time.sleep(0.5)
        ws_url = [t for t in tabs if t["type"] == "page"][0]["webSocketDebuggerUrl"]
        ws = websocket.create_connection(ws_url, timeout=60)
        mid = [0]
        def send(method, params=None):
            mid[0] += 1; ws.send(json.dumps({"id": mid[0], "method": method, "params": params or {}})); return mid[0]
        send("Network.enable"); send("Page.enable")
        send("Page.navigate", {"url": url})
        want, got, pending = {}, [], {}
        t_end = time.time() + 40 + scrolls * 6; next_scroll = time.time() + 15; done_scrolls = 0
        ws.settimeout(1.0)
        while time.time() < t_end:
            if time.time() > next_scroll and done_scrolls < scrolls:
                send("Runtime.evaluate", {"expression": "window.scrollTo(0, document.body.scrollHeight); document.querySelectorAll('button').forEach(b=>{if(/more|load|show/i.test(b.innerText)) b.click()})"})
                done_scrolls += 1; next_scroll = time.time() + 6
            try:
                m = json.loads(ws.recv())
            except Exception:
                continue
            if m.get("method") == "Network.responseReceived":
                r = m["params"]["response"]
                if match in r["url"]:
                    want[m["params"]["requestId"]] = r["url"]
            elif m.get("method") == "Network.loadingFinished" and m["params"]["requestId"] in want:
                rid = m["params"]["requestId"]; pending[send("Network.getResponseBody", {"requestId": rid})] = rid
            elif "id" in m and m["id"] in pending:
                rid = pending.pop(m["id"])
                body = m.get("result", {}).get("body", "")
                got.append({"url": want[rid], "body": body})
                print("captured", want[rid], len(body), flush=True)
        json.dump(got, open(out, "w", encoding="utf-8"), ensure_ascii=False)
        print("responses:", len(got))
    finally:
        p.kill()


if __name__ == "__main__":
    main()
