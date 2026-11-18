# API ideas — btc-race-24h-20261118-1444

Per Gadiel's standing tactic: study the top leaderboard first, then get idea
references from his APIs, compare, build only the best with Muse Spark.

## What was studied first

- Previous race btc-race-24h-20261117-0603 (4,387 entries): top 15 ALL
  dip-buy / mean-reversion bots. Winner "Stabilised dip-buy cbBTC bot v2":
  +2.42%, 4 trades, drawdown 0.64%.
- Our v2 "Acute Proton" (deep-dip rider): dev +$39.86 on the previous
  window, but only +$2.11 / rank 859 on its race window.
- This race's dev window: BTC $65,083 → $63,261 (−2.80%), buy-and-hold
  −$28.00, largest dip from rolling high 3.24%, per-minute vol 0.067%.

## API responses (same brief to all five, 2026-11-18 evening)

| API / model | Result | Idea |
|---|---|---|
| Groq `openai/gpt-oss-120b` | Answered | "Deep-dip, fast-revert (60-min high)": entry ≥200 bps below 60-min rolling high + EMA5 > EMA15, $250 layered entries (max 4), TP +180 bps (late +120 after 300 bars), stop −120 bps, trail 70 bps, time stop 480 bars. Claimed $120–$150 on this window (unverified). |
| 100milionseek `deepseek-v4.1-flash-free` | TIMEOUT (60 s) | None — helper slow/unstable tonight, as in the gta6 v3 session. |
| OpenRouter `nvidia/nemotron-3-ultra-550b-a55b:free` | "None" | None — known helper parsing issue (model returns, helper prints None). |
| CoArena `deepseek-v4-1-flash-1017` | "None" | None — same helper parsing issue. |
| Numes `moonshotai/kimi-k3.1-pro:free` | No reply in session | None — call still running when the build moved on; result not awaited. |

## Adopted / rejected (all verified against the dev window by simulation, not taken on trust)

- ADOPTED (from Groq): the **rolling-high dip** entry — ≥200–250 bps below
  the 60-min rolling high. The scan found D=250, TP=150 the best single
  trigger (+$11.13, 1 round trip). Groq's "83% of bars ≥1% below the high"
  was wrong (it is 83 bars, not 83%) — the trigger was re-derived from the
  data, not from his numbers.
- ADOPTED (from Groq, reshaped): a **tighter TP** (150 bps instead of the
  v2 bot's 210) — the window's best legs are +150–280 bps, so 150 banks
  them; 180–210 mostly never fires.
- REJECTED (from Groq): **layered $250 entries / 4 concurrent positions** —
  RULES.txt allows at most 1 open position. Invalid under the rules.
- REJECTED (from Groq): **EMA5 > EMA15 filter** — untested claim of ">70%
  hit rate"; the scan showed the plain dip trigger already isolates the
  events, and the filter adds a failure mode with no measured gain.
- REJECTED (from Groq): **stop-loss −120 bps / trail 70 bps** — the scan
  found trail 120 bps (not 70) keeps the bot in the slow recovery leg;
  a 70-bps trail exits it early and a hard −120 stop adds nothing over
  the trail.
- ADOPTED (own measurement, not from any API): the **momentum-recovery**
  trigger (ret30 ≥ +80 while ≥100 bps below the rolling high) and the
  **R60 dip only from bar 120** (the bar-60 entry buys the opening drop
  itself and loses ~$15). Both were found by scanning this window and
  cross-checked on the previous race's dev window.
- The final bot was chosen by a two-window test, not by any single API:
  it is the only candidate positive on BOTH dev windows (+$24.01 this
  race, +$27.39 previous race) with trades on both.
