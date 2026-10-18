"""Walk-forward verdict (docs/BD_WF_PLAN.md, amended): the test windows' dollar P&L chained on ONE continuous
balance of $24,895 at the fixed lot (additive, no compounding), with the floating equity rebuilt minute by
minute from each report (guardian_sim, validated); the same for the base runs. Writes the daily paths and
the verdict to docs/evidence so the result can be reproduced from the repository.
Usage: python research/bd_wf/aggregate.py BARS_CSV"""
import json, os, sys
import numpy as np, pandas as pd
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "research", "btc"))
import guardian_sim as g  # noqa: E402

TERM = r"C:\MT5_JEV_TEST"
EV = os.path.join(ROOT, "docs", "evidence")
DEP, WINDOWS = 24895.0, (5, 6, 7)


def path(kind, bars):
    """Continuous floating equity (minute lows) of the chained windows, and per-window results."""
    bal, parts, per = DEP, [], {}
    for i in WINDOWS:
        rep = os.path.join(TERM, f"bdwf_w{i}_{kind}.htm")
        evf = os.path.join(EV, f"bdwf_w{i}_{kind}.json")
        if not os.path.exists(rep) or not os.path.exists(evf):
            return None, {"missing": f"bdwf_w{i}_{kind}"}
        # the report must be the one the verified evidence was made from (review PR #25)
        import hashlib
        if hashlib.sha256(open(rep, "rb").read()).hexdigest() != json.load(open(evf, encoding="utf-8")).get("report_sha256"):
            return None, {"report_changed": f"bdwf_w{i}_{kind}"}
        pos, left = g.pair(g.deals(rep))
        if left:
            return None, {"unpaired": f"bdwf_w{i}_{kind}", "left": left}
        tt, lo, _ = g.equity_path(pos, bars.time.values, bars.low.values, bars.high.values, 0.0)
        s = pd.Series(lo, index=pd.to_datetime(tt, unit="s")) + bal
        pk = s.cummax().clip(lower=bal); dd_w = float(((s - pk) / pk).min() * 100)   # seeded at the opening balance (review)
        net = float(pos.net.sum())
        per[i] = {"net": round(net, 2), "max_dd_pct_in_window": round(dd_w, 1), "wiped": bool(s.min() <= DEP * 0.1)}
        parts.append(s); bal += net
    p = pd.concat(parts)
    return p, per


def main():
    bars = pd.read_csv(sys.argv[1])
    out = {}
    for kind in ("test", "base"):
        p, per = path(kind, bars)
        if p is None:
            out[kind] = per; continue
        pk = p.cummax().clip(lower=DEP); dd = float(((p - pk) / pk).min() * 100)
        yrs = (pd.Timestamp("2026-10-01") - pd.Timestamp("2026-01-01")).days / 365.25   # the registered 9 months (review)
        total = sum(v["net"] for v in per.values())
        ann = total / DEP / yrs * 100
        out[kind] = {"windows": per, "total_net": round(total, 2), "simple_annual_pct": round(ann, 1),
                     "max_dd_pct_chained": round(dd, 1),
                     "passes": all(not v["wiped"] and v["max_dd_pct_in_window"] >= -30 for v in per.values()) and dd >= -30 and ann >= 50}
        p.resample("1D").min().to_csv(os.path.join(EV, f"bdwf_{kind}_daily_low.csv"))
    if "total_net" in out.get("test", {}) and "total_net" in out.get("base", {}):
        out["test_beats_base"] = out["test"]["total_net"] > out["base"]["total_net"]
        # the registered verdict needs BOTH: the thresholds and beating the base (review PR #25)
        out["verdict_success"] = bool(out["test"]["passes"] and out["test_beats_base"])
    else:
        # a missing/changed/unpaired report means the verdict was NOT computed - never a valid failure (review PR #25)
        out["status"] = "incomplete"; out["verdict_success"] = None
    out.setdefault("status", "complete")
    json.dump(out, open(os.path.join(EV, "bdwf_verdict.json"), "w"), indent=1)
    print(json.dumps(out, indent=1))
    if out["status"] != "complete":
        sys.exit(2)


if __name__ == "__main__":
    main()
