"""Lars (EA Black Dragon, bd.set) segments per account from the user's tracking Excel, joined to the live deals.
A segment = one Excel row whose settings are 'Lars': start date, initial lot, protection floor; it ends at the next row of the same sheet.
Live P&L per segment = realized trading cash of ALL magics in [start, end) (protection closes come under magic 0), from the read-only deals export.
Writes data/derived/lars/segments.csv (git-ignored: holds balances). Prints no account numbers.
Usage: py -3.12 research/fleet/lars_segments.py"""
import re, glob, json, os
import pandas as pd

XL = "bots/manual_report.xlsx"


def num(pat, s):
    m = re.search(pat, str(s)); return float(m.group(1)) if m else None


def rows():
    out = []
    x = pd.ExcelFile(XL)
    for sh in x.sheet_names:
        if not sh.startswith("#"): continue
        n = int(re.match(r"#(\d+)", sh).group(1))
        d = x.parse(sh, header=None).iloc[3:]
        d = d[pd.to_datetime(d[8], format="%d.%m.%Y", errors="coerce").notna()]
        for r in d.itertuples(index=False):
            out.append(dict(acct=n, broker=r[2], start=pd.to_datetime(r[8], format="%d.%m.%Y"), bot=str(r[9]), sets=str(r[10]), tf=str(r[11]),
                            bal_xl=float(r[5]) if str(r[5]).replace(".", "").isdigit() else None,
                            lot=num(r"(0\.\d+)", r[16]),
                            floor=num(r"(\d{4,6})", r[16]) if "הגנה" in str(r[16]) else None, note=str(r[15]) + " | " + str(r[16])))
    s = pd.DataFrame(out).sort_values(["acct", "start"], kind="stable")
    s["end"] = s.groupby("acct").start.shift(-1)
    s = s[s.end.isna() | (s.end > s.start)]                       # same-day duplicate rows: keep the last of the day
    s = s.drop_duplicates(["acct", "start"], keep="last")
    s["end"] = s.groupby("acct").start.shift(-1)
    s["lars"] = s.sets.str.strip().eq("Lars") & s.bot.str.contains("Black Dragon")
    return s


def live(s):
    res = []
    for r in s.itertuples():
        g = sorted(glob.glob(f"data/raw/{'btc_bot_4' if r.acct == 4 else f'black_dragon_{r.acct}'}/2026*"))
        if not g: res.append((None, None, None)); continue
        m = json.load(open(g[-1] + "/manifest.json")); k = 100   # every fleet account is a cent account (Excel "סנטים"); RoboForex labels them USD
        x = pd.read_csv(g[-1] + "/deals.csv"); x["t"] = pd.to_datetime(x.time, unit="s")
        end = r.end if pd.notna(r.end) else pd.Timestamp("2026-07-16")
        w = x[(x.t >= r.start) & (x.t < end)]
        tr = w[w.type <= 1]; cash = (tr.profit + tr.swap + tr.commission) / k
        prot = tr.comment.fillna("").str.match(r"^n_.*_v")
        lot0 = tr[(tr.entry == 0) & (tr.magic == 5555)].volume.min() if len(tr) else None
        res.append((round(float(cash.sum())), round(float(cash[prot].sum())), lot0))
    s[["live_pnl", "live_prot_pnl", "live_min_lot"]] = pd.DataFrame(res, index=s.index)
    return s


if __name__ == "__main__":
    s = live(rows())
    os.makedirs("data/derived/lars", exist_ok=True); s.to_csv("data/derived/lars/segments.csv", index=False)
    L = s[s.lars]
    print(L[["acct", "broker", "start", "end", "tf", "lot", "floor", "live_pnl", "live_prot_pnl", "live_min_lot"]].to_string(index=False))
