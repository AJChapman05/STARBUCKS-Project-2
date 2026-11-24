# Project 2 — Meridian Portfolio Mandate Engine

**AI use:** I used OpenAI Codex to assist with implementation, testing, stress analysis, and draft documentation. The Locked Changed-Input Record uses an **AI-assisted pre-run prediction, prepared with Codex under the instructor's in-class permission**; that permission was given verbally in class.

**Ownership and purpose:** The analysis and decision are mine. This work is educational and is not investment advice.

This runnable Streamlit app compares three portfolios using the Lab 13 investable universe: an equal-weight baseline, a 60/40 global-equity/investment-grade-bond **comparison benchmark**, and a BAA point-in-time signal-selected constrained portfolio. The app does not convert the benchmark into a hard constraint.

## Setup, run, and test

From this directory:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python analysis.py
pytest -q
streamlit run app.py
```

Open the local URL printed by Streamlit. A clean user must run `python analysis.py` before `streamlit run app.py`; it produces the frozen display contract consumed by the app.

## What the app shows

- All three portfolios' nonzero weights, planning return/risk status, and every mandate verdict with its reason.
- The Lab 13 seven-year horizon, annual rebalancing instruction, and CPI + 4% net-of-cost rolling-five-year objective. The objective is visibly `NOT TESTABLE` because CPI and sourced portfolio-cost inputs are unavailable.
- Explicit warnings for failed liquidity, reserve, issuer, missing-risk, borrowing, turnover, and cost checks.
- The constrained-versus-benchmark gross expected-return comparison, labeled as a planning estimate rather than a net-of-cost conclusion.
- A point-in-time BAA data card with formula, dates, availability rule, transformations, missing-data rule, timing, universe, and look-ahead/survivorship limits.
- Four required stress runs: estimate downshift, shorter BAA window, transaction-cost feasibility, and constraint completeness. Each shows base/stress weights, results, risk, cost status, and mandate-status groups.
- S4, S9, and S10 as unresolved committee items, never as passed requirements.

## Project map and output flow

| Path | Purpose |
|---|---|
| `analysis.py` | The only portfolio calculation engine; validates inputs and writes the display contract. |
| `app.py` | Streamlit presentation only; reads `visible_output.json` and performs no finance calculations. |
| `data/point_in_time_baa.csv` | Course-documented BAA observations and conservative availability dates. |
| `data/transaction_cost_training_input.csv` | Intact 10-bps Week 11 training input, used only as a transaction-cost feasibility probe. |
| `docs/point-in-time-signal-data-card.md` | Source, timing, and bias documentation. |
| `docs/course-input-register.md` | Course-source inventory and intentionally unavailable inputs. |
| `docs/stress-analysis.md` | Stress design, results boundary, and measurable stop condition. |
| `docs/locked-changed-input-record.md` | Completed local one-input record with the AI-assisted prediction, immutable pre-run commit, changed-case evidence, reconciliation, and baseline restoration. |
| `tests/` | Engine and Streamlit visible-result tests. |
| `visible_output.json` | Generated, frozen visible output. Regenerate with `python analysis.py`. |
| `stress_output.json` | Generated stress results. Regenerate with `python analysis.py`. |
| `docs/decision-memo.md` | Draft rejection recommendation and committee ask. |
| `docs/validation-and-ai-use.md` | Validation/AI register, including the completed local Locked Changed-Input Record and publication limitation. |
| `project-submission-manifest.csv` | Submission manifest draft with no invented links, video details, or access checks. |

The traceable flow is: course facts and data → `analysis.py` → tests → `visible_output.json` and `stress_output.json` → `app.py`.

## Required video opening (for each future video)

No videos or transcripts have been created. At the opening of each future video, say these two statements accurately:

1. “I used OpenAI Codex to assist with implementation, testing, stress analysis, and draft documentation. The Locked Changed-Input Record uses an AI-assisted pre-run prediction, prepared with Codex under the instructor's in-class permission; that permission was given verbally in class.”
2. “The analysis and decision are mine. This work is educational and is not investment advice.”

## Evidence categories and interpretation boundary

| Category | What belongs here | Where it is shown |
|---|---|---|
| Sourced course facts | Holdings, candidate weights, reserve/liquidity/issuer rules, planning return/risk inputs, and BAA metadata/observations | `docs/course-input-register.md`, `data/`, and the source paths listed below |
| Student judgments | Cash uses the Treasury-bill planning proxy; a positive BAA change selects A rather than D; 60/40 remains a comparison benchmark | `visible_output.json` → `student_judgments` |
| Model outputs | Portfolio weights, mandate verdicts, BAA change, planning return/risk, benchmark comparison, and stress results | `visible_output.json` and `stress_output.json` |
| Unresolved mandate choices | S4 benchmark role, S9 loss rule, S10 optimization/preferences, borrowing, turnover, CPI, and costs | App warnings, `visible_output.json` → `scorability`, and the limitations below |

Course-source paths:

- `../mandate.py` and `../lab-13.md`: holdings, candidate weights, reserve/liquidity/issuer restrictions, and S4/S9/S10 classification.
- `../portfolio.py`: course planning returns, volatility, and correlations for Treasury bills, Treasury notes, the IG fund, and global equity fund.
- `../lab-17-point-in-time/data_card.md`: BAA metadata, values, frequency, source, and release-time boundary.

## Known limitations and unresolved mandate choices

- No CPI series or sourced costs: the CPI + 4% **net** objective cannot be tested.
- No prior approved weights: annual turnover cannot be calculated.
- S4 is unresolved: the committee must confirm whether 60/40 is solely a comparison benchmark or the intended strategic allocation.
- S9 is unresolved: it lacks a risk measure, test method, probability/window, and breach procedure.
- S10 is unresolved: the optimization target and sector, ESG, tax, and home-bias preferences are unspecified.
- No course total-return/risk estimate exists for private real estate or Acme instruments, so equal-weight return/risk is intentionally unscorable.
- This is a planning engine, not a backtest or investment recommendation.
- Dedicated Project 2 GitHub repository: https://github.com/AJChapman05/STARBUCKS-Project-2. The earlier pre-run push to the parent course repository was blocked; the Locked Changed-Input Record documents that the required pre-run GitHub publication was not achieved.
