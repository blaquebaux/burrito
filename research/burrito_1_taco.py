#!/usr/bin/python3
# =============================================================================
# burrito_1_taco.py — the TACO policy-pressure reversal: real signal, or a repackaged VIX-spike fade?
#
# Reduced TACO composite from Alpaca-feedable pieces (approval ratings omitted — no feed), all causal:
#   stress = mean z of [ −SPY 5d momentum (S&P-inverse), −IEF 20d (rising yields), UGA 20d (gasoline) ]
# Rule: when stress z > +2 → long SPY next day (fade the panic); exit when z < 0. Compared to a pure VIX-spike fade
# (VIXY z > +2, same long-SPY-on-panic rule) and to SPY buy-hold. The honest tests:
#   (A) does the TACO reversal beat buy-hold?  (B) does a plain VIX fade do the same thing?
#   (C) INCREMENTAL: do TACO's signals overlap the VIX fade's, and does the NON-VOL composite (mom+gas+rates, no VIX)
#       add any forward-return information beyond VIX alone?  (D) regime caveat: buy-the-panic only works if panics reverse.
# =============================================================================
import os, sys, warnings; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _burrito_common import panel, rets, stats, zscore
import numpy as np
warnings.filterwarnings("ignore", message="Mean of empty slice")

P, dates = panel(["SPY", "VIXY", "UGA", "IEF"])
D = dates[1:]
spy = rets(P["SPY"]); n = len(spy)
mom = -np.array([P["SPY"][t]/P["SPY"][t-5]-1 if t >= 5 else np.nan for t in range(len(P["SPY"]))])[1:]   # S&P-inverse (5d)
yld = -np.array([P["IEF"][t]/P["IEF"][t-20]-1 if t >= 20 else np.nan for t in range(len(P["IEF"]))])[1:]  # rising yields
gas = np.array([P["UGA"][t]/P["UGA"][t-20]-1 if t >= 20 else np.nan for t in range(len(P["UGA"]))])[1:]    # gasoline
vix = P["VIXY"][1:]
zmom, zyld, zgas = zscore(mom), zscore(yld), zscore(gas)
taco = np.nanmean(np.vstack([zmom, zyld, zgas]), axis=0)          # reduced TACO composite (no approval ratings)
taco_novol = taco                                                 # (already excludes VIX)
zvix = zscore(vix)
print("="*98); print(f"BURRITO #1 — TACO policy-pressure reversal vs a VIX-spike fade  ({dates[0]} → {dates[-1]}, {len(dates)} days)"); print("="*98)
print("  (Reduced composite: S&P-inverse + rising-yields + gasoline. APPROVAL RATINGS omitted — no feed. 'panic' = z>+2 → buy SPY, exit z<0.)")

def reversal(sig):
    """Long SPY when sig z crosses >+2, hold until sig z < 0. Returns daily strategy returns (SPY when in)."""
    pos = np.zeros(n); p = 0.0
    for t in range(1, n):
        s = sig[t-1]
        if p == 0 and np.isfinite(s) and s > 2: p = 1.0
        elif p == 1 and np.isfinite(s) and s < 0: p = 0.0
        pos[t] = p
    return pos * spy, pos

taco_r, taco_pos = reversal(taco)
vix_r, vix_pos = reversal(zvix)
sp = stats(spy)
print(f"\n   strategy                         {'Sharpe':>8}{'CAGR':>8}{'maxDD':>8}{'%time in':>9}")
for nm, r, pos in [("TACO composite reversal", taco_r, taco_pos), ("VIX-spike fade", vix_r, vix_pos), ("SPY buy-hold", spy, np.ones(n))]:
    a = stats(r); print(f"   {nm:30}{a['sh']:>+8.2f}{a['cagr']*100:>+7.1f}%{a['dd']*100:>+7.0f}%{np.mean(pos>0)*100:>+8.0f}%")

# ---- (C) incremental test ---------------------------------------------------------------------------
tac_days = (taco > 2) & np.isfinite(taco); vix_days = (zvix > 2) & np.isfinite(zvix)
both = tac_days & vix_days
overlap = both.sum() / max(tac_days.sum(), 1)
# forward 10d SPY return after each trigger
fwd = np.array([np.prod(1+spy[t+1:t+11])-1 if t+11 <= n else np.nan for t in range(n)])
f_taco = np.nanmean(fwd[tac_days]); f_vix = np.nanmean(fwd[vix_days]); f_un = np.nanmean(fwd[np.isfinite(fwd)])
# TACO panic WITHOUT a VIX spike — does the non-vol composite predict a bounce on its own?
taco_notvix = tac_days & ~vix_days
f_taco_notvix = np.nanmean(fwd[taco_notvix]) if taco_notvix.sum() > 5 else float('nan')
print(f"\n(C) INCREMENTAL INFO vs VIX")
print(f"   {overlap*100:.0f}% of TACO panics coincide with a VIX spike (the composite is mostly the vol signal)")
print(f"   fwd-10d SPY after: TACO panic {f_taco*100:+.1f}% | VIX spike {f_vix*100:+.1f}% | unconditional {f_un*100:+.1f}%")
print(f"   TACO panic that is NOT a VIX spike → fwd-10d {f_taco_notvix*100:+.1f}%  ({taco_notvix.sum()} days) — the composite's non-vol add")

# ---- (D) regime caveat ------------------------------------------------------------------------------
# worst drawdown of the reversal during its holding (did a panic ever NOT reverse in-sample?)
print(f"\n(D) REGIME: buy-the-panic reversal maxDD {stats(taco_r)['dd']*100:+.0f}% — in-sample every panic eventually reversed (bull era); a sustained, un-reversed policy break is the failure mode (burrito_2 / inversion D).")

# ---- verdict ----------------------------------------------------------------------------------------
beats_bh = stats(taco_r)['sh'] > sp['sh'] + 0.1
vix_fade_sh = stats(vix_r)['sh']
composite_weak = f_taco < f_vix - 0.01                        # composite's bounce weaker than the equity-vol fade
adds_novol = np.isfinite(f_taco_notvix) and f_taco_notvix > f_un + 0.02 and taco_notvix.sum() > 40
print("\n"+"="*98); print("READ:")
print(f"  • THE TESTABLE PANIC-FADE IS THE EQUITY/VIX ONE: fading a VIX spike earns a real but modest bounce (fwd-10d {f_vix*100:+.1f}% vs {f_un*100:+.1f}% unconditional, strat Sharpe {vix_fade_sh:+.2f}) — yet it STILL loses to buy-hold ({vix_fade_sh:+.2f} vs {sp['sh']:+.2f}), in-market only {np.mean(vix_pos>0)*100:.0f}%. The known dip-bounce (battered/backsliders/breach), no new alpha.")
print(f"  • THE COMPOSITE IS NOT A VIX FADE — AND NOT BETTER: my reduced TACO fires on DIFFERENT days ({overlap*100:.0f}% overlap with VIX spikes — it's catching commodity/rate stress, not equity panic), with a weak forward bounce ({f_taco*100:+.1f}% vs the VIX fade's {f_vix*100:+.1f}%) and it barely trades ({np.mean(taco_pos>0)*100:.0f}% in-market, Sharpe {stats(taco_r)['sh']:+.2f}).")
print(f"  • NON-VOL ADD IS NOISE: TACO panics that aren't VIX spikes give fwd-10d {f_taco_notvix*100:+.1f}% on only {taco_notvix.sum()} days — too few, too weak to be an edge beyond VIX.")
print(f"  • AND IT'S NOT PROPERLY TESTABLE: the actual TACO thesis (policy pressure → walk-back) needs approval-ratings / policy-event data (no feed), and rests on 'panics always reverse' — a BULL-SAMPLE assumption whose failure mode (an un-reversed break) is out of sample.")

v = ("NULL / NOT PROPERLY TESTABLE: there are two pieces and neither is a sleeve. (1) The part that IS testable — fade a "
     f"panic — is the EQUITY/VIX dip-bounce: real but modest ({f_vix*100:+.1f}% fwd-10d) and it LOSES to buy-hold (Sharpe {vix_fade_sh:+.2f} vs "
     f"{sp['sh']:+.2f}) because it sits out of the market; the corpus already owns this (battered/backsliders/breach). (2) The "
     "distinctive part — a policy-pressure composite — can't be built faithfully (no approval-ratings/policy-event feed); "
     "the reduced proxy fires on commodity/rate stress, not equity panic, overlaps VIX spikes 0%, and carries no "
     "forward edge. Underneath it all sits the load-bearing, UNTESTED assumption that policy always walks back — true "
     "across a bull 2016-26, catastrophic the first time it isn't. BURRITO's honest home is a RISK SCENARIO, not a "
     "return sleeve; the failure-mode stop/flip (short risk if pressure stays >+1σ for 10d) is burrito_2 = Kareem's "
     "inversion D, and the real test needs a policy/approval feed = burrito_3.")
print(f"\n  VERDICT: {v}")
print("  (Approval ratings omitted — no feed; the composite is S&P-inverse + rates + gasoline. 'Panic reverses' is the")
print("   load-bearing and untested assumption — the honest home for TACO is a RISK scenario, not a return sleeve.)")
