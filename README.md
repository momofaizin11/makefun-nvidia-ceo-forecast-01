# Next-CEO-of-NVIDIA price forecaster (make.fun entry)

`python3 -P -s main.py` reads every `*.in` case in `$MAKEFUN_INPUT_DIR` (else
`/input`) and writes one `<id>.out` per case to `$MAKEFUN_OUTPUT_DIR` (else
`/output`). Stdlib only, no network, no clock, no randomness: two runs on the same case
give byte-identical output. Per market it writes 240 rows of five quantiles,
row h-1 for minute at+h. The median sits at the checkpoint price x (no drift
is fitted) and the spread widens like a random walk's:

- `s0` = sample stdev (n-1) of the consecutive differences of the last 120
  prices, floored at 0.0005 (0.0005 outright when the tail has under 3 points)
- `s = 0.51 * s0`, `w(h) = s * h ** 0.45`
- five values `x + k * w` for `k = -2.6, -0.6, -0.2, +0.2, +2.8` (levels
  0.05/0.25/0.50/0.75/0.95), each clamped to [0, 1] and rounded to 6 decimals

Local grade (`work/local_grade.py`, 2 runs per case): p00 0.445247,
p01 0.308282, p02 0.380895, p03 0.231657, p04 0.193514, p05 0.105570.

    PRACTICE LOSS 0.266095  median error 0.716671  coverage 0.887891
    slowest case 0.05 s of the 8 s budget; house baseline 0.363589 on it
