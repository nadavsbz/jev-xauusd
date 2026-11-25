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


PROT = r"^n_[\d.]+_v$"   # the user's equity-floor tool closes (Grok t376/t384 review)


def start_of(x, r, nxt):
    ins = x[(x.type <= 1) & (x.entry == 0) & (x.magic == 5555) & (x.t >= r.start) & (x.t < nxt)]
    if not len(ins): return None, None
    m = ins[(ins.volume - (r.lot or -1)).abs() < 0.005]
    return (m if len(m) else ins).t.iloc[0], bool(len(m))


def live(s):
    """t384 v2 boundaries: start = first 5555 entry with the row's lot on/after the Excel date (else the first 5555 entry);
    cut_L = first protection close after start; end = min(cut_L, next row start). Live P&L = realized cash of positions
    opened by 5555 inside [start, end) plus their protection closes; flags for positions open at start/end."""
    res = []
    for r in s.itertuples():
        g = sorted(glob.glob(f"data/raw/{'btc_bot_4' if r.acct == 4 else f'black_dragon_{r.acct}'}/2026*"))
        if not g: res.append({}); continue
        k = 100   # every fleet account is a cent account (Excel "סנטים"); RoboForex labels them USD
        x = pd.read_csv(g[-1] + "/deals.csv"); x["t"] = pd.to_datetime(x.time, unit="s"); x = x.sort_values(["time", "ticket"])
        nxt = r.end if pd.notna(r.end) else pd.Timestamp("2026-07-16")
        st, matched = start_of(x, r, nxt)
        if st is None: res.append({}); continue
        nr = s[(s.acct == r.acct) & (s.start == r.end)]                # the next row: its own live start bounds this one
        if pd.notna(r.end) and len(nr):
            n2 = nr.iloc[0]; n_end = n2.end if pd.notna(n2.end) else pd.Timestamp("2026-07-16")
            if n2.lars: ns, _ = start_of(x, n2, n_end); nxt = ns if ns is not None else nxt
            else: nxt = r.end + pd.Timedelta(days=1)                    # next row is another bot: keep that day (a cut may close this Lars run)
        ins = x[(x.type <= 1) & (x.entry == 0) & (x.magic == 5555) & (x.t >= st) & (x.t < nxt)]
        cuts = x[(x.type <= 1) & (x.t >= st) & (x.t < nxt) & x.comment.fillna("").str.match(PROT)]
        cut = cuts.t.iloc[0] if len(cuts) else None
        en = cut + pd.Timedelta(minutes=5) if cut is not None else nxt   # noqa
        pos = set(x[(x.type <= 1) & (x.entry == 0) & (x.magic == 5555) & (x.t >= st) & (x.t < en)].position_id)
        tr = x[(x.type <= 1) & x.position_id.isin(pos) & (x.t >= st) & (x.t < en)]
        cash = (tr.profit + tr.swap + tr.commission) / k
        opened_before = set(x[(x.type <= 1) & (x.entry == 0) & (x.magic == 5555) & (x.t < st)].position_id)
        closed_after = set(x[(x.type <= 1) & (x.entry != 0) & (x.t >= st)].position_id)
        exits = tr[tr.entry != 0].groupby("position_id").volume.sum(); entries = tr[tr.entry == 0].groupby("position_id").volume.sum()
        res.append(dict(start_live=st, cut_live=cut, end_live=en, live_pnl=round(float(cash.sum()), 2),
                        live_prot_pnl=round(float(cash[tr.comment.fillna("").str.match(PROT)].sum()), 2),
                        live_min_lot=float(ins.volume.min()), lot_matched=matched,
                        open_at_start=bool(opened_before & closed_after), open_at_end=bool((entries - exits.reindex(entries.index).fillna(0) > 1e-9).any()),
                        n_type2=int(((x.type == 2) & (x.t >= st) & (x.t < en)).sum())))
    return s.join(pd.DataFrame(res, index=s.index))


if __name__ == "__main__":
    s = rows(); s = live(s)
    os.makedirs("data/derived/lars", exist_ok=True); s.to_csv("data/derived/lars/segments.csv", index=False)
    L = s[s.lars]
    T = L[(L.broker == "roboforex") & (L.tf == "15M") & (L.end <= pd.Timestamp("2026-07-16"))].copy()
    T.to_csv("data/derived/lars/segments_t384.csv", index=False)
    print(T[["acct", "start", "start_live", "cut_live", "end_live", "lot", "lot_matched", "floor", "live_pnl", "open_at_start", "open_at_end", "n_type2"]].to_string(index=False))
