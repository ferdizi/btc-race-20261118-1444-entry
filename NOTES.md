# Study notes — btc-race-24h-20261118-1444

## Dev window (this race, 17 Nov 14:44 UTC → 18 Nov 14:44 UTC, 1,440 bars)

- BTC $65,083.31 → $63,260.75 (−2.80%). Buy-and-hold PnL −$28.00.
- Per-minute return vol 0.067% (~2.5% daily). 613 up / 680 down / 146 flat bars.
- Buy-and-hold max drawdown −3.24% (bar 1436). Largest dip from rolling high 3.24%.
- Only two tradeable events: the opening dip (bars 0–70, −2.5%, bounce +159 bps
  within 120 bars from the bar-68 trough) and the slow recovery leg (+277 bps
  from the bar-133 trough to bar 508, ~6 hours).
- Best forward legs anywhere: +30 bars +107 bps, +60 +118, +120 +183, +240 +222,
  +400 +241. No +300 bps leg exists in the window.

## Previous race (btc-race-24h-20261117-0603, 4,387 entries, final)

Top 15 ALL dip-buy / mean-reversion, +1.91% to +2.42%, 2–18 trades:
1. Stabilised dip-buy cbBTC bot v2 — +2.42%, 4 trades, DD 0.64%
2. Dip-buy CBBTC bot — +2.38%, 4 trades
3. Dip-buy swing bot: CBBTC 1-minute mean reversion — +2.29%, 8 trades
4. Range-dip mean-reversion BTC bot v4 — +2.16%, 4 trades
5. dip-buy + regime filter — +2.15%, 4 trades
Our v2 "Acute Proton": race rank 859, PnL +$2.11, 6 trades.

## Scan results (simulator mirrors the harness fill model: 4 bps fee, 2 bps
## slippage, constant-product impact vs open depth, fills at next open)

- v2 formula on THIS window (ret60 ≤ −110, TP 210, trail 90, tstop 400):
  −$6.48. All ret60 variants −$6 to −$8. The deep-dip reversion legs do
  not exist here — dips drift sideways or fall further.
- Rolling-high dip D=250, TP=150: +$11.13 (1 round trip, the bar-68 dip).
- Momentum breakout ret30 ≥ +80, TP=100, trail=120: +$7.35 (1 round trip).
- Combined dip + momentum (D=250, MOM=80, TP=150, trail=120, tstop=600):
  +$24.01 — but −$28.04 on the previous window (momentum buys breakouts
  that reverse on range windows).
- Momentum with below-high filter (only while ≥100 bps below the 60-min
  high): 0 trades on the previous window — the filter kills the losing
  breakout buys while keeping the recovery-leg trade on this window.
- Final (R60 ≤ −110 from bar 120 + rhigh ≥ 250 + mom ≥ +80 below 100,
  TP 150, trail 120, tstop 600): dev18 +$24.01 (4 trades), dev17 +$27.39
  (5 trades), both 2x-fee positive (+$22.37 / +$24.93), DD ≤ 1.53%.
- Sharp-peak warning: D=200/TP=150 is −$8.11 while D=250/TP=150 is +$24.01
  on this window — the final parameters were chosen on the SUM of both
  windows, not on this window alone, and the R60-min-bar rule (120) is a
  plateau (120–180 give the same result), not a tuned point.
