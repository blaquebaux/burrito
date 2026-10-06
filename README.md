# Blaque Baux Burrito

**The "TACO Index" policy-pressure reversal — a distinct signal, or a repackaged VIX-spike fade? Neither: a dip-bounce plus an untestable assumption.**

The "TACO Index" (Trump Always Chickens Out) is a composite of S&P-inverse, Treasury yields, gasoline and approval
ratings that flags "extreme policy pressure then walk-back": at +2σ, buy risk assets; exit on reversion. Burrito tests
Kareem's honest null — is it anything more than a VIX-spike fade? We rebuild a reduced composite from the pieces Alpaca
can feed (S&P-inverse momentum, rising yields via IEF, gasoline via UGA; **approval ratings omitted — no feed**), race it
against a pure VIX fade, and check whether the non-vol composite adds any information.

> **Not investment advice.** Educational/research software. See [DISCLAIMER](DISCLAIMER.md) and [LICENSE](LICENSE).

```bash
python3 research/burrito_1_taco.py   # needs Alpaca data keys in the environment
```

## The finding (two pieces, neither a sleeve)

[`research/burrito_1_taco.py`](research/burrito_1_taco.py) — SPY/VIXY/UGA/IEF, causal, 2016–2026.

| strategy | Sharpe | CAGR | maxDD | % time in |
|---|---|---|---|---|
| TACO composite reversal | +0.07 | +0.2% | −6% | 1% |
| VIX-spike fade | +0.47 | +4.2% | −22% | 7% |
| SPY buy-hold | **+0.88** | +15.0% | −34% | 100% |

- **The *testable* panic-fade is the equity/VIX one** — fading a VIX spike earns a real but modest bounce (forward-10d
  **+4.7% vs +0.6%** unconditional) yet **still loses to buy-hold** (Sharpe +0.47 vs +0.88) because it sits out of the
  market. That's the dip-bounce `battered`/`backsliders`/`breach` already own — no new alpha.
- **The composite is *not* a VIX fade — and not better.** My reduced TACO fires on *different* days (**0% overlap** with
  VIX spikes — it's catching commodity/rate stress, not equity panic), with a weak forward bounce (+1.3%) and it barely
  trades. The non-vol ingredients (rates, gasoline) add noise, not edge (20 non-VIX signal days).
- **The real thesis isn't properly testable here.** The actual policy-pressure signal needs approval-ratings /
  policy-event data (no feed), and it rests on the load-bearing assumption that *panic always walks back* — true across a
  bull 2016–26, catastrophic the first time it isn't (the un-reversed structural break is out of sample).

## Verdict

**NULL / NOT PROPERLY TESTABLE.** Two pieces, neither a return sleeve: the testable "fade the panic" is the known
equity dip-bounce that loses to buy-hold, and the distinctive "policy pressure" composite can't be built faithfully and
shows no edge in reduced form. Underneath sits an untested "always chickens out" assumption that works right up until it
doesn't. Burrito's honest home is a **risk scenario**, not a sleeve. The failure-mode test — flip to *short* risk if
pressure stays above +1σ for 10 days — is a `burrito_2` (Kareem's inversion D); a faithful test needs a policy/approval
feed (`burrito_3`).

## Status

**Research.** Honest null — a viral macro signal checked against the only question that matters (does it beat holding,
and does it add anything over VIX), with its untestable core named plainly. Composite reversal vs VIX fade, signal-overlap
and incremental-information tests, regime caveat, Alpaca SIP daily total return. No live capital.
