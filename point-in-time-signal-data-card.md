# Point-in-Time Signal Data Card — BAA yield change

## Purpose and formula

The signal is the change in Moody's Seasoned Baa Corporate Bond Yield (`BAA`), in basis points, from the earliest to the latest usable observation in the stored point-in-time file. At the documented 2026-10-02 decision date: `(6.47% - 6.19%) × 100 = +28 bps`.

This is a credit-condition indicator, not a total-return forecast or tradable-security price. The selection rule is a **student judgment**: a positive BAA change selects Lab 13 Candidate A rather than Candidate D because A has 14% cash/Treasury reserve and 26% in the investment-grade fund, while D has 97% in that fund. The rule does not prove that A will outperform.

## Source facts

- Provider/source: FRED series `BAA`, Moody's Seasoned Baa Corporate Bond Yield; point-in-time vintages are from ALFRED.
- Stored observations: 2026-07-01 = 6.19%, 2026-08-01 = 6.32%, 2026-09-01 = 6.47%.
- Course evidence: `../lab-17-point-in-time/data_card.md` documents those values, monthly frequency, percent units, and that the September observation was released on 2026-10-01.
- Universe: Lab 13 holdings only. The signal changes the selection between candidates A and D; it does not create securities or alter the benchmark.

## Timing, transformations, and missing data

- Decision/rebalance date: 2026-10-02, the next decision day after the documented 2026-10-01 September release. Annual rebalancing remains the mandate frequency; this is the initial documented decision, not a historical performance backtest.
- Availability rule: accept only observations with `available_on` strictly before the decision date. This deliberately avoids assuming an unknown intraday release time.
- Transformations: values remain percentage points until the basis-point subtraction. No imputation, forward fill, or revision overwrite is permitted.
- Missing/invalid data: stop the signal if fewer than two valid observations are available, dates/values cannot be parsed, a yield is nonpositive, or availability precedes observation date.

## Biases and limitations

- Look-ahead risk: current FRED history can include later data and revisions. Use the ALFRED vintage available at each future decision date; do not use a current FRED value merely because its observation month is earlier.
- Survivorship risk: the signal is a single macro/credit series, not a constituent-level security screen. It does not establish that the available fund universe is survivorship-free.
- Costs: no sourced trading-cost input was supplied. The mandate's CPI + 4% **net** objective is therefore not assessed.
- Separation: source facts are the series metadata/observations and Lab 13 holdings; student judgments are the selection rule and cash proxy; model outputs are emitted only by `analysis.py` into `visible_output.json`.
