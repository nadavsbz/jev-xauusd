"""Shared loaders for the Gold Reaper decoding (descriptive work on the GR period only)."""
import numpy as np, pandas as pd
def m1():
    m = pd.read_csv("data/derived/scan/m1/XAUUSD.csv"); m.index = pd.to_datetime(m.time, unit="s")
    return m[~m.index.duplicated()].query("close > 0")[["open", "high", "low", "close"]]
def gr():
    g = pd.read_csv("docs/agents/grok_data/myfxbook/goldreaper_history.csv"); g = g[g.Symbol == "XAUUSD"].copy()
    g["o"] = pd.to_datetime(g["Open Date"], format="%m.%d.%Y %H:%M"); g["c"] = pd.to_datetime(g["Close Date"], format="%m.%d.%Y %H:%M")
    for a, b in (("sl", "SL (pips)"), ("tp", "TP (pips)")): g[a] = pd.to_numeric(g[b].replace("-", np.nan))
    g["q"] = np.where(g.Action == "Buy", 1, -1); g["ret"] = g.q * (g["Close Price"] / g["Open Price"] - 1)
    g["kind"] = np.select([g.tp.notna(), g.sl > 0, g.sl <= 0], ["TP", "SLprofit", "SLloss"], "quick")
    return g.sort_values("o")
def baskets(g):
    return g.groupby(["o", "q"]).agg(px=("Open Price", "mean"), n=("Lots", "size"), ret=("ret", "mean")).reset_index()
