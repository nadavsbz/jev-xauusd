"""Round 84 (prereg docs/prereg/r84_bd_ms20_ddscale.md): BD ms20_h1119 base vs DDScale switch, per year: return, floor cuts, cut cost, win-day sum.
Usage: py -3.12 research/bd1/r84_report.py [hold]"""
import sys, os, numpy as np, pandas as pd
sys.path.insert(0,'research/btc');sys.path.insert(0,'research/stable')
from guardian_sim import deals
HOLD = len(sys.argv) > 1 and sys.argv[1] == "hold"
def yr(f):
    x=deals(f"C:/MT5_JEV_TEST/{f}.htm"); x["day"]=pd.to_datetime(x.t,unit="s").dt.normalize(); x["net"]=x.profit+x.swap+x.commission
    d=x.groupby("day").net.sum(); eq=pd.concat([pd.Series([120000.0]),120000+d.cumsum()]); r=d/(120000+d.cumsum()).shift(1).fillna(120000)
    cut=r[r<-0.02]; ret=eq.iloc[-1]/120000-1; mdd=(eq/eq.cummax()-1).min()
    return ret*100, len(cut), (cut.mean()*100 if len(cut) else 0), r[r>0].sum()*100, mdd*100
rows=[]
years = ["hold"] if HOLD else range(2016,2026)
for y in years:
    row={"y":y}
    for k,f in (("base", "ev14_rf_hold_ms20_h1119" if HOLD else f"{'ev18' if y<=2018 else 'ev12'}_rf{y}_ms20_h1119"),
                ("dd5q", f"ev84_rf{y}_ms20_h1119_dd5q"),("user", "ev86_rf_hold_user" if HOLD else f"ev87_rf{y}_user"),("dd75", "ev85_rf_hold_ms20_h1119_dd75" if HOLD else f"ev84_rf{y}_ms20_h1119_dd75")):
        if not os.path.exists(f"C:/MT5_JEV_TEST/{f}.htm"): continue
        ret,nc,cc,win,mdd=yr(f); row[k]=f"{ret:+.0f}% c{nc}({cc:.0f}) w{win:.0f} dd{mdd:.0f}"; row[k+"_r"]=ret
    rows.append(row)
D=pd.DataFrame(rows).set_index("y"); print(D[[c for c in D if not c.endswith("_r")]].to_string())
if not HOLD:
    F=D.loc[2017:2025]
    for k in ("base","dd5q","dd75","user"):
        if k+"_r" not in F: continue
        r=F[k+"_r"].dropna()/100; print(f"{k}: positive {int((r>0).sum())}/9  worst {r.min()*100:+.0f}  mult x{(1+r).prod():.2f}")
