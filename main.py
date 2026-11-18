"""Tri-trigger dip-rider (btc-race-24h-20261118-1444).

What the dev window (1,440 one-minute cbBTC bars, 17-18 Nov 2026) actually
rewards, measured from scratch in this session before this bot was written:

  * The window falls -2.80% (BTC $65,083 -> $63,261). Buy-and-hold loses
    -$28.00, so it fails the dev gate. There is no free lunch in holding.
  * The previous race's winning formula (deep-dip mean reversion, our v2:
    60-min fall <= -110 bps, TP +210) FAILS here: every ret60 variant
    scores -$6 to -$8. The dips in this window do not revert -- they drift
    sideways or fall further. The window's only two tradeable events are:
      (1) the opening dip: price falls ~2.5% in the first 70 bars, then
          bounces +159 bps within 120 bars (bar 68 trough);
      (2) the slow recovery leg: +277 bps from the bar-133 trough to bar
          508 (about 6 hours), a grind, not a spike.
  * The previous race (20261117-0603) top 15 were ALL dip-buy /
    mean-reversion bots (winner +2.42%, 4 trades). Its dev window was a
    range (+0.49%) where deep dips reverted +170 to +250 bps. So the two
    windows reward OPPOSITE shapes -- a bot tuned to one loses on the
    other. This bot is therefore built to be positive on BOTH dev windows
    (this race's and the previous race's), not just the one it must pass.

Strategy (one position at most, long only, full size): three entry
triggers, each with its own re-arm, sharing one exit set.
  1. R60 dip: 60-minute close return <= -110 bps. Only from bar 120: at
     bar 60 the "60-minute return" is measured from the window's arbitrary
     first bar (the opening drop itself), and buying it costs ~-$15.
     Re-arm when the 60-min return recovers above -80 bps.
  2. Rolling-high dip: close >= 250 bps below the 60-minute rolling high.
     This is the trigger that catches the opening dip (bar 68). Re-arm
     when the dip narrows below 220 bps.
  3. Momentum recovery: 30-minute return >= +80 bps WHILE the close is
     still >= 100 bps below the 60-minute rolling high -- a recovery from
     a dip, never a breakout at a high (breakouts at highs are what lose
     money on range windows). Re-arm when the 30-min return falls below
     +50 bps. This is the trigger that catches the slow recovery leg.
  Exits (whichever comes first):
    - take-profit +150 bps above the entry close,
    - trailing stop 120 bps below the highest close since entry,
    - time stop 600 bars.
  Never open after bar 1380 (final 60 bars): a trade opened there has no
  time to develop and the end flatten just eats its fees.

Verified on the dev window by running this file itself through the wire
protocol (hello/batch/done, the harness's own fill model, two runs
byte-identical): net PnL +$24.01 on $1,000, 2 round trips (4 filled
orders), max drawdown 1.45%, Sharpe +1.30. At doubled fees still +$22.37.
Same parameters on the previous race's dev window: +$27.39, 5 trades
(3 round trips, one flattened at the end), max drawdown 0.72%.
Split-half on this window: 1st +$24.01, 2nd $0.00 (no trades -- the
second half is a slow bleed with no trigger firing, so the bot sits in
cash rather than forcing a losing trade).

Deterministic: integer arithmetic only, no clock, no environment, no
randomness, no files, no network. The only state is the close history
and the position record below.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "vendor"))
import makefun_bars

SYMBOL = "CBBTC"
WINDOW_BARS = 1440  # published window length (RULES.txt: 1,440 bars)
LOOKBACK = 60       # dip measured over this many bars

# Entry 1: 60-minute close return <= -110 bps (only from bar 120: the
# return needs a settled baseline, not the window's opening drop).
DIP_BPS = 110
DIP_MIN_BAR = 120
DIP_REARM_BPS = 80
# Entry 2: close >= 250 bps below the 60-minute rolling high.
HIGH_DIP_BPS = 250
HIGH_DIP_REARM_BPS = 220
# Entry 3: 30-minute return >= +80 bps while still >= 100 bps below the
# 60-minute rolling high (recovery from a dip, not a breakout at a high).
MOM_BPS = 80
MOM_BELOW_HIGH_BPS = 100
MOM_REARM_BPS = 50
# Exits.
TAKE_PROFIT_BPS = 150
TRAIL_BPS = 120
TIME_STOP_BARS = 600
# Do not open in the final 60 bars.
LAST_ENTRY_BAR = WINDOW_BARS - 60
# A buy must be at least 1 USDC (the harness min notional).
MIN_NOTIONAL = 1_000_000
# max_slippage_bps: 500 (5%). A 1-minute gap in dev never exceeded ~80 bps,
# so 500 never blocks a normal entry; it only refuses an absurd fill.
MAX_SLIPPAGE_BPS = 500


def _down_at_least(now, then, bps):
    """True when now is at least `bps` below `then` (integer math)."""
    return now * 10000 <= then * (10000 - bps)


def _up_at_least(now, then, bps):
    """True when now is at least `bps` above `then` (integer math)."""
    return now * 10000 >= then * (10000 + bps)


class Rider:
    """The whole bot state: close history plus the open position, if any."""

    def __init__(self):
        self.closes = []
        self.held = False
        self.entry_bar = -1
        self.entry_close = 0
        self.best_close = 0
        self.armed_dip = True
        self.armed_high = True
        self.armed_mom = True

    def note_fill(self, state, bar_no, close):
        """Reconcile with the real account after each batch.

        A buy/sell the market rejected leaves the flag wrong. A position
        with no flag is re-adopted (its exit is re-evaluated fresh, with
        the normal target); a flag with no position is forgotten.
        """
        pos = state.positions.get(SYMBOL)
        have = pos is not None and pos.qty > 0
        if have and not self.held:
            self.held = True
            self.entry_bar = bar_no
            self.entry_close = close
            self.best_close = close
        elif self.held and not have:
            self.held = False

    def decide(self, state, batch):
        if state.warming_up:
            return []
        if not any(b.get("symbol") == SYMBOL for b in batch.get("bars", [])):
            return []  # gap minute: no bar, the stale close must not count
        close = state.close(SYMBOL)
        if close is None:
            return []
        self.closes.append(close)
        bar_no = len(self.closes) - 1
        self.note_fill(state, bar_no, close)
        if bar_no < LOOKBACK:
            return []

        if self.held:
            # Holding: update the peak, then take-profit, trail, time stop.
            if close > self.best_close:
                self.best_close = close
            done = (
                _up_at_least(close, self.entry_close, TAKE_PROFIT_BPS)
                or _up_at_least(self.best_close, close, TRAIL_BPS)
                or bar_no - self.entry_bar >= TIME_STOP_BARS
            )
            if not done:
                return []
            self.held = False
            held = state.positions.get(SYMBOL)
            if held is None or held.qty <= 0:
                return []
            return [{"side": "sell", "symbol": SYMBOL, "qty": held.qty,
                     "max_slippage_bps": MAX_SLIPPAGE_BPS}]

        # Flat: entry logic. Armed flags update only while flat, exactly
        # as the backtest simulator did.
        if bar_no >= LAST_ENTRY_BAR:
            return []
        if bar_no >= WINDOW_BARS - 1:
            return []  # orders decided on the last batch are rejected
            # (after_end); the harness flattens the position anyway.
        high = max(self.closes[bar_no - LOOKBACK:bar_no])
        dip_rh = (high - close) * 10000 // high

        # Trigger 1: 60-minute dip (settled baseline only).
        if bar_no >= DIP_MIN_BAR:
            r60 = (close * 10000 // self.closes[bar_no - LOOKBACK]) - 10000
            if self.armed_dip and r60 <= -DIP_BPS:
                self.armed_dip = False
                return self._buy(state, bar_no, close)
            if r60 > -DIP_REARM_BPS:
                self.armed_dip = True

        # Trigger 2: deep dip below the 60-minute rolling high.
        if self.armed_high and dip_rh >= HIGH_DIP_BPS:
            self.armed_high = False
            return self._buy(state, bar_no, close)
        if dip_rh < HIGH_DIP_REARM_BPS:
            self.armed_high = True

        # Trigger 3: momentum recovery, still below the rolling high.
        r30 = (close * 10000 // self.closes[bar_no - 30]) - 10000
        if self.armed_mom and r30 >= MOM_BPS and dip_rh >= MOM_BELOW_HIGH_BPS:
            self.armed_mom = False
            return self._buy(state, bar_no, close)
        if r30 < MOM_REARM_BPS:
            self.armed_mom = True
        return []

    def _buy(self, state, bar_no, close):
        amount = min(state.cash, state.weight_room(SYMBOL))
        if amount < MIN_NOTIONAL:
            return []
        self.held = True
        self.entry_bar = bar_no
        self.entry_close = close
        self.best_close = close
        return [{"side": "buy", "symbol": SYMBOL,
                 "notional_quote_units": amount,
                 "max_slippage_bps": MAX_SLIPPAGE_BPS}]


_RIDER = Rider()


def on_batch(state, batch):
    return _RIDER.decide(state, batch)


makefun_bars.run(on_batch)
