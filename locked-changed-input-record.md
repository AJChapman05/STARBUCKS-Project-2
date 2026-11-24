# Locked Changed-Input Record

Status: **COMPLETE LOCALLY / pre-run snapshot, changed case, test result, and baseline restoration preserved. Push remains blocked.**

Instructor permission: AI use for this record was given verbally in class. The prediction below is labeled **AI-assisted pre-run prediction, prepared with Codex under the instructor's in-class permission**. It is not represented as AI-off or solely student-authored.

## Pre-run prediction and single changed input

| Field | Recorded value |
|---|---|
| One changed input and units | BAA signal window; usable monthly observations |
| Old value | 3 usable observations: 2026-07-01 through 2026-09-01 |
| New value | Latest 2 usable observations: 2026-08-01 through 2026-09-01 |
| Numeric signal-selection threshold | 0 bps; this is the existing coded rule in `analysis.py` (`change_bps > 0` selects Candidate A) |
| Prediction label | AI-assisted pre-run prediction, prepared with Codex under the instructor's in-class permission |
| AI-assisted pre-run prediction | “Reducing the BAA signal window from three observations to the latest two will change the signal from +28 bps to +15 bps, based on the existing data. Because the signal remains above the model’s 0 bps selection threshold, Candidate A should remain selected. The committee decision should remain reject/0% because the unresolved mandate gates are unchanged.” |
| Expected portfolio weights | Candidate A should remain selected; expected weights remain 2% Cash, 2% Treasury bills, 10% Treasury 10-year note, 60% Global equity index fund, and 26% Investment-grade bond fund. |
| Expected mandate/decision effect | Coded Candidate A checks should remain unchanged; borrowing, turnover, and S9 should remain `NOT TESTABLE`; S4 and S10 should remain unresolved; decision should remain reject/0%. |
| Prediction recorded | 2026-11-23 20:29:07 MST |
| Pre-run commit/snapshot | `c57340f856542a26b8dcd03c18fae7ce60500dc5` — 2026-11-23 20:31:28 MST — `Project 2: lock AI-assisted BAA window prediction` |
| Snapshot scope | `git show --name-only` confirmed only `project-2-investment-management/` paths in the pre-run commit. |
| Safe push attempt | Not pushed. `git push --dry-run origin main` was blocked: local `main` is 33 commits behind `origin/main`; its ahead range includes unrelated Starbucks/course commits; remote authentication failed with no anonymous write access. No force-push, pull, rebase, or history rewrite was attempted. |

## Preserved baseline before changed execution

| Item | Evidence |
|---|---|
| Baseline configuration | Default `analysis.py` signal window: 3 usable monthly BAA observations |
| Baseline signal/result | +28 bps; Candidate A selected |
| Baseline outputs | `evidence/changed-input-record/baseline-visible_output.json` and `evidence/changed-input-record/baseline-stress_output.json` |
| Baseline test command | `.venv/bin/python analysis.py` followed by `.venv/bin/python -m pytest -q` |
| Baseline test result | 10 passed in 0.75s; `evidence/changed-input-record/baseline-test-results.txt` |

## Required execution sequence

1. Freeze this prediction in Git and record its commit ID and timestamp.
2. Push that commit to the configured GitHub remote and verify the push.
3. Preserve base configuration/output/test result, then execute exactly one changed input.
4. Preserve changed configuration/output/test result and reconcile actual versus predicted direction and threshold.
5. Record decision effect, failure diagnosis if prediction diverges, commit ID, timestamps, and restore the approved base configuration.

## Changed execution result and prediction reconciliation

| Item | Actual result / evidence |
|---|---|
| Changed-case command | `.venv/bin/python evidence/changed-input-record/run_two_observation_changed_case.py` |
| Changed execution timestamp | 2026-11-23 20:33:55 MST |
| Initial execution failure | `ModuleNotFoundError: No module named 'analysis'`; no changed output was produced. The evidence runner was corrected only to locate the project-root engine. See `evidence/changed-input-record/changed-two-observation-test-results.txt`. |
| Actual changed signal | +15 bps, using 2026-08-01 = 6.32% and 2026-09-01 = 6.47%; `evidence/changed-input-record/changed-two-observation-output.json` |
| Actual selection and weights | Candidate A remained selected: 2% Cash, 2% Treasury bills, 10% Treasury 10-year note, 60% Global equity index fund, 26% Investment-grade bond fund. |
| Actual mandate checks | PASS: weights sum, long-only, reserve, liquidity, issuer, derivatives. `NOT TESTABLE`: borrowing, turnover, calendar-year loss. S4/S9/S10 remain unresolved. |
| Actual planning result | Gross expected return 6.67%; volatility 10.148%; constrained-minus-benchmark gross expected return -0.13 percentage points. No net-of-cost conclusion. |
| Prediction reconciliation | Matched: signal changed +28 bps → +15 bps; it stayed above 0 bps; Candidate A, weights, mandate checks, and reject/0% decision remained unchanged. |
| Decision effect | None. The committee decision remains reject/0% because unresolved mandate gates are unchanged. |
| Changed-case test result | `.venv/bin/python -m pytest -q`: 10 passed in 0.70s. Evidence: `evidence/changed-input-record/changed-two-observation-test-results.txt`. |
| Baseline restoration | Verified identical with `cmp -s` for `visible_output.json` and `stress_output.json` against the preserved baseline artifacts. |
| Changed output | `evidence/changed-input-record/changed-two-observation-output.json` |
