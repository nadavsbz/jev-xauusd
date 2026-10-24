"""Clone and tester-BD vs account 1 live baskets, per validation month (docs/BD_CLONE.md, 25.10.2026).
Usage: python research/bd1/clone_vs_live.py DEALS_CSV TAG:FROM:TO [...]
For every month: baskets in live, in val_<tag>_clone, in val_<tag>_bdreal; share of live baskets opened in the
same M15 bar, with the same side, with the same level count, closed within 60 s; net per source."""
import os, sys, json
import pandas as pd
sys.path[:0] = [os.path.join(os.path.dirname(__file__), "..", "btc"), os.path.dirname(__file__)]
import guardian_sim as g
from vol_lot_map import baskets

def live_pos(csv):
    d = pd.read_csv(csv); d = d[(d.magic == 5555) & (d.symbol == "XAUUSDc")]
    ins = d[d.entry == 0].set_index("position_id")
    outs = d[d.entry == 1].groupby("position_id").agg(t1=("time", "max"), pr=("profit", "sum"), sw=("swap", "sum"), cm=("commission", "sum"))
    p = ins.join(outs, how="inner")
    return pd.DataFrame({"side": p.type.map({0: "buy", 1: "sell"}), "vol": p.volume, "t0": p.time, "t1": p.t1,
                         "net": p.pr + p.sw + p.cm + p.commission}).reset_index(drop=True)

def table(pos):
    b = baskets(pos).groupby("basket").agg(t0=("t0", "min"), t1=("t1", "max"), n=("net", "size"), side=("side", "first"), net=("net", "sum"))
    b["bar"] = b.t0 // 900
    return b.drop_duplicates("bar").set_index("bar")

def main():
    live = live_pos(sys.argv[1]); out = {}
    for spec in sys.argv[2:]:
        tag, f, t = spec.split(":"); lo = pd.Timestamp(f).value // 10**9; hi = pd.Timestamp(t).value // 10**9
        L = table(live[(live.t0 >= lo) & (live.t0 < hi)]); row = {"live_baskets": len(L), "live_net": round(float(L.net.sum()))}
        for src in ("clone", "bdreal"):
            p = g.pair(g.deals(f"C:/MT5_JEV_TEST/val_{tag}_{src}.htm"))[0]; C = table(p[(p.t0 >= lo) & (p.t0 < hi)])
            j = L.join(C, rsuffix="_t", how="inner")
            row[src] = {"baskets": len(C), "net": round(float(C.net.sum())), "same_bar": round(len(j) / len(L), 3),
                        "same_side": round(float((j.side == j.side_t).mean()), 3), "same_levels": round(float((j.n == j.n_t).mean()), 3),
                        "exit_60s": round(float(((j.t1 - j.t1_t).abs() <= 60).mean()), 3), "worst_basket": round(float(C.net.min()))}
        out[tag] = row
    print(json.dumps(out, ensure_ascii=False, indent=1))

if __name__ == "__main__":
    main()
