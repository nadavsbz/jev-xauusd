"""Mine the developer's Telegram group (read-only export, data/raw/telegram/toptarget/relevant.jsonl) for
user-REPORTED outcomes: which bot / set file, over how long, and what happened (profit, blown, stopped).
These are claims by group members (self-selected, unverified): they rank candidates for the tester, they
are never evidence of an edge by themselves.

Output (local only, the raw texts stay out of the repository):
  data/derived/telegram/outcomes.csv   one row per message with a bot + an outcome word
  data/derived/telegram/summary.json   counts per bot and per set-file name, positive vs negative
Usage: python research/telegram/mine_results.py"""
import collections, json, os, re
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(ROOT, "data", "raw", "telegram", "toptarget", "relevant.jsonl")
OUT = os.path.join(ROOT, "data", "derived", "telegram")

BOTS = {"black_dragon": r"black\s*dragon|\bbd\b", "hamster": r"hamster", "umbrella": r"umbrell?a",
        "trend_catcher": r"trend\s*catcher", "trend_ai": r"trend\s*ai\b", "btc_bot": r"btc\s*bot",
        "bull_scalper": r"bull\s*scalper", "ultima": r"ultima", "strong_support": r"strong\s*support"}
NEG = r"blown|blew|wiped|margin\s*call|stop\s*out|stopped\s*out|lost\s+(?:all|everything|\d)|drawdown\s+of\s+\d|\bdd\b\s*\d|account\s+(?:is\s+)?(?:gone|dead|burned)|liquidat"
POS = r"profit|gain|\+\s?\d+\s?%|\d+\s?%\s*(?:gain|profit|growth|month)|doubled|running\s+(?:for|since)|still\s+running|survived|steady|consistent"
DUR = r"(\d+)\s*(day|week|month|year)s?"
SET = r"[\w\-\. ]{3,80}\.set\b"


def main():
    os.makedirs(OUT, exist_ok=True)
    rows = []
    for line in open(SRC, encoding="utf-8"):
        m = json.loads(line); t = (m.get("text") or "").replace("\n", " ")
        low = t.lower()
        if len(low) > 1500 or "rules of the group" in low:
            continue
        bots = [b for b, p in BOTS.items() if re.search(p, low)]
        neg = re.search(NEG, low); pos = re.search(POS, low)
        if not bots or not (neg or pos):
            continue
        dur = re.findall(DUR, low)
        rows.append(dict(id=m["id"], date=m["date"][:10], sender=m.get("from"), bots=";".join(bots),
                         outcome="neg" if neg and not pos else "pos" if pos and not neg else "mixed",
                         duration=";".join(f"{n} {u}" for n, u in dur[:3]),
                         sets=";".join(s.strip() for s in re.findall(SET, t))[:200],
                         dev=bool(m.get("from") == 1708204414), text=t[:300]))
    d = pd.DataFrame(rows)
    d.to_csv(os.path.join(OUT, "outcomes.csv"), index=False, encoding="utf-8")
    summ = {"messages": len(d), "per_bot": {}, "per_set": {}}
    for b in BOTS:
        s = d[d.bots.str.contains(b)]
        if len(s):
            summ["per_bot"][b] = {k: int(v) for k, v in s.outcome.value_counts().items()} | {"senders": int(s.sender.nunique())}
    sets = collections.defaultdict(collections.Counter)
    for r in d.itertuples():
        for s in filter(None, r.sets.split(";")):
            sets[s.lower()][r.outcome] += 1
    summ["per_set"] = {k: dict(v) for k, v in sorted(sets.items(), key=lambda kv: -sum(kv[1].values()))[:40]}
    json.dump(summ, open(os.path.join(OUT, "summary.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print(json.dumps(summ["per_bot"], indent=1))
    print(len(summ["per_set"]), "set names with outcomes")


if __name__ == "__main__":
    main()
