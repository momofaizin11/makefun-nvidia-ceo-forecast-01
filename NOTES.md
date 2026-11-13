# Why this model

The house baseline writes `x + z * 0.0025 * sqrt(h)`: a fixed spread, normal
tails, no drift. On the practice prices that spread is too wide and the tails
are the wrong shape: it pays at quiet minutes and still misses the jumps.

Four fixes, all measured on the practice windows:

1. Scale the spread to each market: tick sizes of a thin candidate and of the
   front-runner differ by an order of magnitude, so the sample stdev of the
   last 120 one-minute changes (n-1, floored at 0.0005) sets it per market.
2. Shrink it to 0.54 x s0: prices move in steps, so consecutive changes are
   correlated and the raw tick stdev overstates a 4-hour walk's spread.
3. Bend the time law to h ** 0.45, slightly concave because the price
   mean-reverts inside the checkpoint window.
4. Skew the levels: `-2.9, -0.85, -0.2, +0.05, +2.2` sit closer to the median
   than the normal z's with fatter outer tails, the down one fatter than up.

The tick volatility is now measured on two windows, the last 120 changes and
the last 600 (a shorter series uses all it has), and the calmer of the two —
the smaller stdev — sets the spread; on the practice windows the quieter long
window was the better guide than either window alone. It is scaled by 0.54 and
read off the new quantile multipliers `-2.9, -0.85, -0.2, +0.05, +2.2`, which
keep the fat down tail while pulling the outer reaches in.

No drift is fitted: the checkpoint price predicts itself best one step ahead.
The model reads only the case it is given, so the run is reproducible.