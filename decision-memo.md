# Decision Memo — Reject Adoption Pending Mandate Completion

**AI use:** I used OpenAI Codex to assist with implementation, testing, stress analysis, draft documentation, and the pre-run prediction in the Locked Changed-Input Record. My instructor verbally permitted AI use for that record in class. The prediction is disclosed as AI-assisted, not AI-off or solely student-authored.

**Ownership and purpose:** The analysis and decision are mine. This work is educational and is not investment advice.

## Decision and committee ask

**Recommendation: reject adoption, allocation, and rebalancing at this time.** The allocation range approved for implementation is **0% to the process and 0% to every candidate portfolio** until the mandate is made testable. This is a process rejection, not a claim that Candidate A, D, or the 60/40 benchmark is permanently unsuitable.

The committee should resolve S4, S9, and S10; supply prior approved weights, a sourced cost convention, and evidence on borrowing; then request a rerun before considering a pilot or allocation.

## Evidence categories

- **Sourced facts:** Lab 13 supplies the holdings, candidate weights, reserve/liquidity/issuer rules, and mandate classifications. The course planning inputs supply the stated returns, volatilities, and correlations. The stored BAA observations support the point-in-time signal.
- **Student judgments:** Cash is proxied by Treasury bills for planning estimates; a positive BAA change selects Candidate A rather than D; the 60/40 mix remains a comparison benchmark rather than a hard allocation rule.
- **Model outputs:** The engine calculates candidate weights, coded mandate results, the BAA change, planning return/risk, and stress outputs.
- **Unresolved choices and limitations:** S4, S9, S10, external borrowing, turnover, CPI, and sourced portfolio costs are not filled in by the model and are not treated as passes.

## Evidence and result

As of the stored 2026-10-02 decision date, the point-in-time BAA signal rose 28 bps from 6.19% (2026-07-01) to 6.47% (2026-09-01). The stated student rule selected Lab 13 Candidate A: 2% cash, 2% Treasury bills, 10% Treasury 10-year note, 60% global equity index fund, and 26% investment-grade bond fund.

Candidate A passes the coded weight, long-only, reserve (14% versus 3%), liquidity (100% versus 90%), issuer (0% Acme versus 8%), and non-derivative checks. Its planning-only gross expected return is 6.67% and volatility is 10.15%. It trails the 60/40 comparison benchmark's planning gross expected return by 0.13 percentage points. These are not net-of-cost results; cash is proxied by Treasury bills for the planning estimate.

The 60/40 benchmark remains a comparison benchmark, not a hard allocation constraint. It fails the 3% reserve rule at 0%. Equal weight fails liquidity (87.5%) and combined Acme concentration (25%).

## Why adoption is not ready

The engine's measurable process gate is: **stop implementation whenever any mandatory mandate rule is `FAIL` or `NOT TESTABLE`.** Candidate A retains `NOT TESTABLE` outcomes for external borrowing, turnover (no prior approved weights), and S9 calendar-year loss. S4 is unresolved because the CIO has not said whether 60/40 is strategic allocation or performance comparison. S10 has no optimization target or preferences. Costs and CPI inputs are absent, so CPI + 4% net of costs cannot be assessed.

Stress analysis reinforces the rejection. A disclosed 100-bps estimate downshift lowered Candidate A's gross planning return to 5.67%, while volatility and coded mandate checks remained unchanged. A two-observation BAA window still selected A (+15 bps). The 10-bps course training cost is infeasible as a portfolio deduction without sourced turnover and cost evidence. Constraint completeness produces `STOP`.

## Monitoring, reversal triggers, and next review

Before each annual rebalance decision, monitor BAA vintage availability and revisions, reserve/liquidity/issuer results, prior approved weights, external-borrowing evidence, CPI/cost evidence, and each unresolved mandate statement. Reopen the decision only when all of the following are evidenced and rerun:

- S4 is explicitly classified by the CIO; if strategic, impose the approved allocation rule.
- S9 has a measure, horizon/probability or scenario method, monitoring frequency, and breach action.
- S10 specifies the optimization target and any sector, ESG, tax, or home-bias preferences.
- Prior approved weights and external-borrowing evidence permit turnover and borrowing tests.
- CPI and cost inputs support a net-of-cost objective test.

Any failure of reserve, five-day liquidity, issuer aggregation, long-only, non-derivative, or the completed S9/turnover/borrowing tests reverses a future pilot/allocation decision to reject or pause.

**Next review point:** the first committee meeting after all five evidence conditions above are documented, and before any allocation, pilot, or rebalance is executed. No calendar date is asserted because none was supplied.

See `docs/validation-and-ai-use.md` for test evidence and the completed local Locked Changed-Input Record. Its pre-run commit could not be safely pushed to GitHub, so repository publication remains incomplete.
