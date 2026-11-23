"""Public, guest-readable Sponser forum pages -> posts of one author (JSONL, data/ is git-ignored).
Polite: one page every 3s, generic UA, stops on any non-200. Stores only the extracted posts, not the pages.
Usage: py -3.12 research/social/sponser_crawl.py <forumid> <pid_from> <pid_to> <author>"""
import html, json, os, re, sys, time, urllib.request

FORUM, P0, P1, AUTHOR = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
OUT = f"data/raw/sponser/f{FORUM}_{P0}_{P1}.jsonl"; os.makedirs("data/raw/sponser", exist_ok=True)
CARD = re.compile(r'forum\.toggleMsgBody\((\d+)\)">(.*?)</h2>.*?<address[^>]*>(.*?)</address>\s*<time datetime="\[([^\]]+)\]".*?'
                  r'<div class="hide msg-body-\1"[^>]*>(.*?)<footer', re.S)
seen = set()
if os.path.exists(OUT):
    for l in open(OUT, encoding="utf-8"): seen.add(json.loads(l)["id"])
f = open(OUT, "a", encoding="utf-8"); n_pages = n_posts = 0
for pid in range(P1, P0 - 1, -1):
    url = f"https://m.sponser.co.il/forum.php?forumid={FORUM}&pid={pid}"
    try:
        r = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 research-client"}), timeout=30)
        if r.status != 200: print("stop status", r.status, pid); break
        t = r.read().decode("utf-8", "replace")
    except Exception as e:
        print("stop error", pid, str(e)[:80]); break
    for mid, subj, auth, ts, body in CARD.findall(t):
        if html.unescape(auth).strip() != AUTHOR or mid in seen: continue
        imgs = re.findall(r'data-src="([^"]+ForumFiles[^"]+)"', body)
        txt = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", body))).strip()
        f.write(json.dumps(dict(id=mid, pid=pid, ts=ts, subject=re.sub(r"<[^>]+>", "", html.unescape(subj)).strip(), text=txt, images=len(imgs)), ensure_ascii=False) + "\n")
        seen.add(mid); n_posts += 1
    n_pages += 1
    if n_pages % 50 == 0: f.flush(); print(pid, n_pages, n_posts, flush=True)
    time.sleep(3)
print("done pages", n_pages, "posts", n_posts)
