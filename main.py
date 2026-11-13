#!/usr/bin/env python3
"""Forecast the next 240 one-minute Yes prices of every market in a case.

Model: the price stays at its checkpoint value x, with a spread that grows as
h ** 0.45, scaled by a fraction of the market's own recent tick volatility.
Output: <id>.out with one object {"forecasts": [{"id": ..., "q": [[5 numbers] * 240]}]}.
"""
import json
import math
import os

HORIZONS_DEFAULT = 240
TAILS = (120, 600)
SIGMA_SCALE = 0.54
WIDTH_EXP = 0.45
K = (-2.9, -0.85, -0.2, 0.05, 2.2)
FLOOR_SIGMA = 0.0005


def tail_prices(prices, tail):
    """At most the last `tail` points; a shorter series drops its first point."""
    if len(prices) > tail:
        return prices[-tail:]
    return prices[1:]


def window_sigma(prices, tail):
    tail = tail_prices(prices, tail)
    if len(tail) < 3:
        return FLOOR_SIGMA
    diffs = [tail[i + 1] - tail[i] for i in range(len(tail) - 1)]
    n = len(diffs)
    mean = sum(diffs) / n
    var = sum((d - mean) ** 2 for d in diffs) / (n - 1)
    s0 = math.sqrt(var)
    if s0 < FLOOR_SIGMA:
        return FLOOR_SIGMA
    return s0


def tick_sigma(prices):
    """The calmer of the short (120) and long (600) tick volatilities."""
    return min(window_sigma(prices, t) for t in TAILS)


def quantile_rows(x, s, horizon):
    rows = []
    for h in range(1, horizon + 1):
        w = s * (h ** WIDTH_EXP)
        row = []
        for k in K:
            v = x + k * w
            if v < 0.0:
                v = 0.0
            elif v > 1.0:
                v = 1.0
            row.append(math.floor(v * 1000000.0 + 0.5) / 1000000.0)
        rows.append(row)
    return rows


def forecast_market(market, horizon):
    prices = market.get("prices") or []
    if not prices:
        x = 0.5
        s = FLOOR_SIGMA
    else:
        x = prices[-1]
        s = SIGMA_SCALE * tick_sigma(prices)
    return {"id": market["id"], "q": quantile_rows(x, s, horizon)}


def read_case(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    in_dir = os.environ.get("MAKEFUN_INPUT_DIR") or "/input"
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    try:
        names = sorted(n for n in os.listdir(in_dir) if n.endswith(".in"))
    except OSError:
        names = []
    if names:
        os.makedirs(out_dir, exist_ok=True)
    for name in names:
        case = read_case(os.path.join(in_dir, name))
        horizon = int(case.get("horizon_minutes") or HORIZONS_DEFAULT)
        if horizon < 1:
            horizon = HORIZONS_DEFAULT
        forecasts = [forecast_market(m, horizon) for m in case.get("markets") or []]
        payload = json.dumps({"forecasts": forecasts}, separators=(",", ":"),
                             ensure_ascii=False)
        out_path = os.path.join(out_dir, name[:-3] + ".out")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(payload)


if __name__ == "__main__":
    main()