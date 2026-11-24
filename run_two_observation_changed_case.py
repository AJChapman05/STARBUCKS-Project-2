"""Generate the one approved changed-input case without altering baseline inputs."""
from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import analysis


OUTPUT = Path(__file__).with_name("changed-two-observation-output.json")


def main() -> None:
    changed = analysis.build_output()
    signal = analysis.baa_signal(window_observations=2)
    weights, selection_reason = analysis.constrained_portfolio(signal)
    constrained = analysis.portfolio_record("Signal-selected constrained portfolio", weights)
    benchmark_return = changed["portfolios"][1]["planning_metrics"]["gross_expected_return"]
    constrained_return = constrained["planning_metrics"]["gross_expected_return"]

    if signal["change_bps"] != 15.0:
        raise AssertionError(f"Expected +15.0 bps, got {signal['change_bps']}.")
    if weights != analysis.candidate_a():
        raise AssertionError("Expected Candidate A to remain selected.")

    changed["changed_input"] = {
        "name": "BAA signal window",
        "old_value": 3,
        "new_value": 2,
        "units": "usable monthly observations",
        "selection_threshold_bps": 0,
        "baseline_evidence": "evidence/changed-input-record/baseline-visible_output.json",
    }
    changed["signal"] = signal
    changed["signal_data_card"] = analysis.signal_data_card(signal)
    changed["selection_reason"] = selection_reason
    changed["portfolios"][2] = constrained
    changed["benchmark_comparison"] = {
        "constrained_minus_benchmark_gross_expected_return": round(constrained_return - benchmark_return, 6),
        "interpretation": "Planning estimate only; no net-of-cost conclusion.",
    }
    OUTPUT.write_text(json.dumps(changed, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Wrote {OUTPUT}")
    print("Changed-case checks: +15.0 bps; Candidate A selected; baseline configuration untouched.")


if __name__ == "__main__":
    main()
