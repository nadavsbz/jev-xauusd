"""BD Overlap pair closes in a tester report: two same-side positions closed in the same second, one of them the newest.
For each: pair net, oldest loss, same-side and total open counts just before. Fits the real Overlap trigger rule."""
import os, sys
import pandas as pd
sys.path[:0] = [os.path.join(os.path.dirname(__file__), "..", "btc")]
import guardian_sim as g

def events(name):
    p = g.pair(g.deals(f"C:/MT5_JEV_TEST/{name}.htm"))[0].reset_index(drop=True)
    out = []
    for t1, grp in p.groupby("t1"):
        for side, s in grp.groupby("side"):
            if len(s) != 2: continue
            openb = p[(p.t0 <= t1) & (p.t1 >= t1)]                    # open at t1 (incl. the pair)
            same = openb[openb.side == side]
            if len(s) == len(same): continue                           # whole basket closed = trailing, not overlap
            new, old = s.sort_values("t0").iloc[1], s.sort_values("t0").iloc[0]
            out.append({"t1": pd.to_datetime(t1, unit="s"), "side": side, "n_side": len(same), "n_all": len(openb),
                        "pair_net": round(s.net.sum(), 2), "old_loss": round(old.net, 2), "new_vol": new.vol, "old_vol": old.vol,
                        "pct": round(100 * s.net.sum() / -old.net, 2) if old.net < 0 else None})
    return pd.DataFrame(out)

if __name__ == "__main__":
    e = events(sys.argv[1])
    pd.set_option("display.width", 200)
    print(e.to_string()); print(e[["n_side", "n_all"]].describe().loc[["min", "50%", "max"]])
