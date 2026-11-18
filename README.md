# Tri-Trigger Dip-Rider — btc-race-24h-20261118-1444

[![make.fun · btc-race-24h-20261118-1444](https://make.fun/badge/btc-race-24h-20261118-1444.svg)](https://make.fun/bounty/btc-race-24h-20261118-1444?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261118-1444)
[![rank](https://make.fun/badge/btc-race-24h-20261118-1444/ferdizi/btc-race-20261118-1444-entry/rank.svg)](https://make.fun/bounty/btc-race-24h-20261118-1444/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261118-1444)
[![reward](https://make.fun/badge/btc-race-24h-20261118-1444/ferdizi/btc-race-20261118-1444-entry/reward.svg)](https://make.fun/bounty/btc-race-24h-20261118-1444?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261118-1444)

A cbBTC paper-trading bot for the make.fun 24-hour BTC race. Long only, $1,000 start, 1-minute bars, full size, one position at most.

## Strategy

Three entry triggers share one exit set (take-profit +150 bps, trailing stop 120 bps, time stop 600 bars, no entry after bar 1380):

1. **60-min dip** — 60-minute close return ≤ −110 bps, only from bar 120 (the return needs a settled baseline, not the window's opening drop).
2. **Rolling-high dip** — close ≥ 250 bps below the 60-minute rolling high.
3. **Momentum recovery** — 30-minute return ≥ +80 bps while the close is still ≥ 100 bps below the 60-minute rolling high (a recovery from a dip, never a breakout at a high).

See `main.py` for the full reasoning, measured from the dev window before the bot was written.

## Verified results (wire-protocol replay, harness fill model, two runs byte-identical)

| Window | Net PnL | Trades | Max DD | Sharpe | 2x-fee PnL |
|---|---|---|---|---|---|
| This race dev (17–18 Nov 2026) | **+$24.01** | 4 | 1.45% | +1.30 | +$22.37 |
| Previous race dev (20261117-0603) | **+$27.39** | 5 | 0.72% | +1.55 | +$24.93 |

Dev gate: net PnL > $0 after all fees — passed on both windows. Deterministic: two runs produce byte-identical replies.

## Layout

- `main.py` — the bot (Python 3.13, stdlib only)
- `vendor/makefun_bars.py` — kit SDK shim, byte-for-byte copy (excluded from authorship counts per RULES.txt)
- `IDEAS.md` — which API model gave which idea, what was adopted or rejected
- `NOTES.md` — study notes: dev-window stats, previous-race formula, scan results

## Grade locally

```sh
node <kit>/cli/makefun.mjs grade-local --kit <kit> --bot <this repo> --driver docker
```
