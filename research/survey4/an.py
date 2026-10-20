import json, sys, numpy as np, pandas as pd
D = sys.argv[1]; REPO = sys.argv[2]
def load(t):
    r = json.load(open(f"{D}/{t}.json"))["chart"]["result"][0]
    s = pd.Series(r["indicators"]["adjclose"][0]["adjclose"], index=pd.to_datetime(r["timestamp"], unit="s").normalize())
    return s.dropna()[lambda x: ~x.index.duplicated()]
T = "DBMF KMLM CTA AQMIX ASFYX RPAR GLD SPY EFA VEU AGG IEF SHY VNQ DBC TLT QQQ".split()
P = {t: load(t) for t in T}
def st(eq):
    eq = eq.dropna(); r = eq.pct_change().dropna()
    yrs = (eq.index[-1]-eq.index[0]).days/365.25
    yr = eq.resample("YE").last(); yr = pd.concat([eq.iloc[:1], yr]).pct_change().dropna()
    return dict(start=str(eq.index[0].date()), cagr=round((eq.iloc[-1]/eq.iloc[0])**(1/yrs)*100-100,1),
                mdd=round((eq/eq.cummax()-1).min()*100,1), vol=round(r.std()*np.sqrt(252)*100,1),
                worst_year=f"{yr.idxmin().year}:{yr.min()*100:.1f}", years=round(yrs,1))
print("== funds (adj close, full history) ==")
for t in "DBMF KMLM CTA AQMIX ASFYX RPAR GLD SPY".split(): print(t, st(P[t]))
# correlations, weekly returns, common window per fund
g = P["GLD"]; s = P["SPY"]
print("== corr (weekly) and gold trend days ==")
gd = g.pct_change()
for t in "DBMF KMLM CTA AQMIX ASFYX RPAR".split():
    df = pd.concat([P[t], g, s], axis=1, keys=["x","g","s"]).dropna()
    w = df.resample("W-FRI").last().pct_change().dropna()
    d = df.pct_change().dropna()
    big = d[d.g.abs() >= 0.03]; up = big[big.g > 0]; dn = big[big.g < 0]
    m = df.resample("ME").last().pct_change().dropna(); bm = m[m.g.abs() >= 0.06]
    print(t, "from", df.index[0].date(), "corrW gold %.2f spy %.2f" % (w.x.corr(w.g), w.x.corr(w.s)),
          "| gold|>=3%% days n=%d mean %.2f%% (up n=%d %.2f%%, down n=%d %.2f%%)" % (len(big), big.x.mean()*100, len(up), up.x.mean()*100, len(dn), dn.x.mean()*100),
          "| gold|>=6%% months n=%d mean %.2f%% hit %d" % (len(bm), bm.x.mean()*100, (bm.x>0).sum()))
# account 1 realised daily
o = pd.read_csv(f"{REPO}/data/derived/bd1/clusters_strict.csv")
o["day"] = pd.to_datetime(o.t1, unit="s").dt.normalize()
a = o.groupby("day").pnl_pct.sum()/100; trough = o.groupby("day").mae_pct.min()/100
print("== vs account1 realised daily", a.index.min().date(), a.index.max().date())
for t in "DBMF KMLM CTA AQMIX ASFYX RPAR SPY GLD".split():
    x = P[t].pct_change()
    df = pd.concat([x, a, trough], axis=1, keys=["x","a","tr"]).dropna()
    bad = df[df.tr <= df.tr.quantile(0.1)]
    print(t, "n=%d corr %.2f | worst-10%% trough days n=%d etf mean %.2f%%" % (len(df), df.x.corr(df.a), len(bad), bad.x.mean()*100))
# strategy backtests, monthly
M = pd.DataFrame({t: P[t].resample("ME").last() for t in T})
R = M.pct_change()
def eqs(r): return (1+r.fillna(0)).cumprod()
# GEM: SPY vs EFA 12m, abs vs SHY, else AGG
mom = M.pct_change(12)
gem = []
for i in range(len(M)-1):
    d = M.index[i]
    if pd.isna(mom.loc[d, ["SPY","EFA","SHY"]]).any() or pd.isna(R.iloc[i+1][["SPY","EFA","AGG"]]).any(): gem.append(np.nan); continue
    win = "SPY" if mom.loc[d,"SPY"] >= mom.loc[d,"EFA"] else "EFA"          # relative first (review PR #23)
    pick = win if mom.loc[d, win] > mom.loc[d,"SHY"] else "AGG"            # then the winner vs SHY
    gem.append(R.iloc[i+1][pick] - 0.0005)
gem = pd.Series(gem, index=M.index[1:]).dropna()
# GTAA5: SPY EFA IEF VNQ DBC, 10m SMA else SHY, 20% each
sma = M.rolling(10).mean(); A5 = ["SPY","EFA","IEF","VNQ","DBC"]; gt = []
for i in range(len(M)-1):
    d = M.index[i]; nx = R.iloc[i+1]
    if pd.isna(sma.loc[d, A5]).any() or pd.isna(nx[A5+["SHY"]]).any(): gt.append(np.nan); continue
    gt.append(sum(0.2*(nx[a] if M.loc[d,a] > sma.loc[d,a] else nx["SHY"]) for a in A5) - 0.0003)
gt = pd.Series(gt, index=M.index[1:]).dropna()
def mst(r, name):
    e = eqs(r); yrs = len(r)/12; yr = r.groupby(r.index.year).apply(lambda x: (1+x).prod()-1)
    print(name, "%s..%s CAGR %.1f%% MDD(monthly) %.1f%% vol %.1f%% worst %d:%.1f%%" % (r.index[0].date(), r.index[-1].date(), (e.iloc[-1]**(1/yrs)-1)*100, (e/e.cummax()-1).min()*100, r.std()*np.sqrt(12)*100, yr.idxmin(), yr.min()*100))
    return r
print("== own backtests (monthly, costs 5bp/3bp per month approx) ==")
mst(gem, "GEM"); mst(gt, "GTAA5")
start = max(gem.index[0], gt.index[0])
mst(gem[gem.index>=start], "GEM same window"); mst(gt[gt.index>=start], "GTAA5 same")
mst(R.SPY[R.index>=start], "SPY same"); mst((0.6*R.SPY+0.4*R.IEF)[R.index>=start], "60/40 same")
mst(R.GLD[R.index>=start], "GLD same")
post = pd.Timestamp("2013-03-01")
mst(gt[gt.index>=post], "GTAA5 post-2013-update"); mst(gem[gem.index>=pd.Timestamp("2014-12-01")], "GEM post-book(2014-11)")
mst(R.SPY[R.index>=pd.Timestamp("2014-12-01")], "SPY post 2014-12")
# monthly corr to gold & trend months
for nm, r in [("GEM", gem), ("GTAA5", gt)]:
    df = pd.concat([r, R.GLD, R.SPY], axis=1, keys=["x","g","s"]).dropna(); bm = df[df.g.abs()>=0.06]
    print(nm, "corrM gold %.2f spy %.2f | gold|>=6%% months n=%d mean %.2f%%" % (df.x.corr(df.g), df.x.corr(df.s), len(bm), bm.x.mean()*100))
# vol-targeted SPY daily: target 12%, 20d vol lagged, cap 1.5, cost 2bp per unit turnover, financing at SHY ret for leverage
r = P["SPY"].pct_change(); rf = P["SHY"].pct_change().reindex(r.index).fillna(0)
vol = r.rolling(20).std().shift(1)*np.sqrt(252); w = (0.12/vol).clip(upper=1.5)
vt = (w*r + (1-w)*rf - w.diff().abs()*0.0002).dropna()
for nm, x in [("VT-SPY 12%", vt), ("SPY", r.reindex(vt.index))]:
    print(nm, st((1+x).cumprod()))
print("== blends, monthly rebalance ==")
def blend(parts, start, name):
    df = pd.concat([p for p,_ in parts], axis=1).dropna(); df = df[df.index > start]
    r = sum(w*df.iloc[:,i] for i,(_,w) in enumerate(parts)); mst(r, name)
s0 = pd.Timestamp("2019-06-30"); s1 = pd.Timestamp("2010-02-28")
blend([(R.DBMF,0.5),(gt,0.5)], s0, "50 DBMF / 50 GTAA5")
blend([(R.DBMF,0.5),(R.SPY,0.5)], s0, "50 DBMF / 50 SPY")
blend([(R.DBMF,1.0)], s0, "DBMF")
blend([(gt,1.0)], s0, "GTAA5 2019+")
blend([(R.AQMIX,0.5),(gt,0.5)], s1, "50 AQMIX / 50 GTAA5 2010+")
blend([(R.AQMIX,0.5),(R.SPY,0.5)], s1, "50 AQMIX / 50 SPY 2010+")
blend([(R.AQMIX,0.4),(R.SPY,0.3),(R.IEF,0.3)], s1, "40 AQMIX/30 SPY/30 IEF 2010+")
