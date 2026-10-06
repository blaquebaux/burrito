#!/usr/bin/python3
# =============================================================================
# _burrito_common.py — shared helpers for Blaque Baux BURRITO (the "TACO Index" policy-pressure reversal).
# Alpaca SIP daily bars (adjustment=all → total return); env keys. Read-only.
#
# The "TACO Index" (Trump Always Chickens Out) is a composite of S&P-inverse, Treasury yields, gasoline and
# approval ratings meant to flag "extreme policy pressure then walk-back": at +2σ, panic has hit a policy
# tolerance threshold → buy risk assets; exit on reversion. BURRITO tests the honest null Kareem posed: is this
# anything more than a repackaged VIX-SPIKE FADE? We rebuild a REDUCED composite from the pieces Alpaca can feed —
# S&P-inverse (−SPY momentum), rates (−IEF = rising yields), gasoline (UGA) — and omit approval ratings (no feed,
# flagged). We then race it against a pure vol-spike fade (VIXY) and, critically, test whether the NON-VOL part of
# the composite adds any incremental information over VIX alone. Prior from the corpus: "buy the panic" is the
# dip-bounce battered/backsliders/breach already own, and it only looks good in a sample where every panic reversed.
# =============================================================================
import os, json, urllib.request, math
import numpy as np

H = {"APCA-API-KEY-ID": os.environ["ALPACA_KEY_ID"], "APCA-API-SECRET-KEY": os.environ["ALPACA_SECRET_KEY"]}
START, END = "2016-01-01", "2026-08-01"
_cache = {}

def bars(s):
    if s in _cache: return _cache[s]
    u = (f"https://data.alpaca.markets/v2/stocks/bars?symbols={s}&timeframe=1Day"
         f"&start={START}&end={END}&adjustment=all&feed=sip&limit=10000")
    try:
        d = json.load(urllib.request.urlopen(urllib.request.Request(u, headers=H), timeout=40))
        _cache[s] = {b["t"][:10]: b["c"] for b in d.get("bars", {}).get(s, [])}
    except Exception:
        _cache[s] = {}
    return _cache[s]

def panel(syms):
    D = {s: bars(s) for s in syms}; D = {s: v for s, v in D.items() if len(v) > 250}
    if not D: return {}, []
    u = list(D); dates = sorted(set.intersection(*[set(D[s]) for s in u]))
    return {s: np.array([D[s][d] for d in dates], float) for s in u}, dates

def rets(px): return px[1:] / px[:-1] - 1

def stats(r):
    r = np.asarray(r, float); r = r[np.isfinite(r)]
    if len(r) < 20 or r.std() == 0: return dict(sh=float('nan'), cagr=float('nan'), dd=float('nan'), vol=float('nan'))
    cum = np.cumprod(1 + r)
    return dict(sh=r.mean()/r.std()*math.sqrt(252), cagr=cum[-1]**(252/len(r))-1,
                dd=float((cum/np.maximum.accumulate(cum)-1).min()), vol=r.std()*math.sqrt(252))

def zscore(x, win=252):
    """Causal trailing z-score (mean/std through t-1)."""
    x = np.asarray(x, float); n = len(x); z = np.full(n, np.nan)
    for t in range(win, n):
        w = x[t-win:t]; m, s = np.nanmean(w), np.nanstd(w)
        if s > 0: z[t] = (x[t] - m) / s
    return z
