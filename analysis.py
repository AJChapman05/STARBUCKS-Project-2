"""Transparent Project 2 portfolio engine.

All material calculations are here.  The Streamlit app only renders the
frozen JSON written by this module.
"""
from __future__ import annotations

import csv
import json
from datetime import date
from math import sqrt
from pathlib import Path
from typing import Any


ROOT = Path(__file__).parent
DATA_PATH = ROOT / "data" / "point_in_time_baa.csv"
TRAINING_COST_PATH = ROOT / "data" / "transaction_cost_training_input.csv"
VISIBLE_OUTPUT_PATH = ROOT / "visible_output.json"
STRESS_OUTPUT_PATH = ROOT / "stress_output.json"

# Facts transcribed from the course's actual Lab 13 checker (mandate.py).
HOLDINGS: dict[str, dict[str, Any]] = {
    "Cash": {"issuer": "none", "days": 0, "reserve": True, "exempt": True, "derivative": False},
    "Treasury bills": {"issuer": "U.S. Treasury", "days": 1, "reserve": True, "exempt": True, "derivative": False},
    "Treasury 10-year note": {"issuer": "U.S. Treasury", "days": 1, "reserve": True, "exempt": True, "derivative": False},
    "Global equity index fund": {"issuer": "diversified fund", "days": 2, "reserve": False, "exempt": True, "derivative": False},
    "Investment-grade bond fund": {"issuer": "diversified fund", "days": 3, "reserve": False, "exempt": True, "derivative": False},
    "Private real estate fund": {"issuer": "diversified fund", "days": 90, "reserve": False, "exempt": True, "derivative": False},
    "Acme Corp bonds": {"issuer": "Acme Corp", "days": 4, "reserve": False, "exempt": False, "derivative": False},
    "Acme Corp stock": {"issuer": "Acme Corp", "days": 1, "reserve": False, "exempt": False, "derivative": False},
}
UNIVERSE = tuple(HOLDINGS)

# Course planning estimates from portfolio.py.  Cash uses the Treasury-bill
# proxy as a disclosed student judgment; no cash-specific return series exists.
SLEEVES = {
    "Treasury bills": {"expected_return": 0.035, "volatility": 0.005},
    "Treasury 10-year note": {"expected_return": 0.043, "volatility": 0.070},
    "Investment-grade bond fund": {"expected_return": 0.050, "volatility": 0.060},
    "Global equity index fund": {"expected_return": 0.080, "volatility": 0.160},
}
CORRELATIONS = {
    "Treasury bills": {"Treasury bills": 1.00, "Treasury 10-year note": 0.10, "Investment-grade bond fund": 0.05, "Global equity index fund": 0.00},
    "Treasury 10-year note": {"Treasury bills": 0.10, "Treasury 10-year note": 1.00, "Investment-grade bond fund": 0.80, "Global equity index fund": -0.10},
    "Investment-grade bond fund": {"Treasury bills": 0.05, "Treasury 10-year note": 0.80, "Investment-grade bond fund": 1.00, "Global equity index fund": 0.25},
    "Global equity index fund": {"Treasury bills": 0.00, "Treasury 10-year note": -0.10, "Investment-grade bond fund": 0.25, "Global equity index fund": 1.00},
}
RETURN_PROXY = {"Cash": "Treasury bills"}

RESERVE_MINIMUM = 0.03  # 4 x $0.75m / $100m
LIQUIDITY_MINIMUM = 0.90
ISSUER_MAXIMUM = 0.08
LIQUIDITY_DAYS = 5
SIGNAL_DECISION_DATE = date(2026, 10, 2)  # next day after documented Sept. release


def check(condition: bool | None, reason: str) -> dict[str, str]:
    return {"status": "PASS" if condition is True else "FAIL" if condition is False else "NOT TESTABLE", "reason": reason}


def validate_weights(weights: dict[str, float]) -> None:
    if set(weights) != set(UNIVERSE):
        missing, extra = set(UNIVERSE) - set(weights), set(weights) - set(UNIVERSE)
        raise ValueError(f"Weights must name exactly the Lab 13 universe; missing={sorted(missing)}, extra={sorted(extra)}")
    if any(not isinstance(value, (int, float)) for value in weights.values()):
        raise ValueError("All weights must be numeric.")


def equal_weight() -> dict[str, float]:
    return {holding: 1 / len(UNIVERSE) for holding in UNIVERSE}


def benchmark_6040() -> dict[str, float]:
    return {holding: 0.60 if holding == "Global equity index fund" else 0.40 if holding == "Investment-grade bond fund" else 0.0 for holding in UNIVERSE}


def candidate_a() -> dict[str, float]:
    # Actual Lab 13 Candidate A, converted from percent to decimal weights.
    values = (0.02, 0.02, 0.10, 0.60, 0.26, 0.0, 0.0, 0.0)
    return dict(zip(UNIVERSE, values))


def candidate_d() -> dict[str, float]:
    values = (0.03, 0.0, 0.0, 0.0, 0.97, 0.0, 0.0, 0.0)
    return dict(zip(UNIVERSE, values))


def load_baa_asof(decision_date: date) -> list[dict[str, Any]]:
    """Use only values published strictly before the decision date.

    The strict rule implements the data card's conservative next-decision-day
    treatment when a release time is unknown.
    """
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Missing point-in-time source file: {DATA_PATH}")
    rows: list[dict[str, Any]] = []
    with DATA_PATH.open(newline="", encoding="utf-8") as stream:
        for raw in csv.DictReader(stream):
            required = {"observation_date", "value_percent", "available_on", "source"}
            if set(raw) != required:
                raise ValueError("BAA data has invalid columns.")
            try:
                available_on = date.fromisoformat(raw["available_on"])
                observation_date = date.fromisoformat(raw["observation_date"])
                value = float(raw["value_percent"])
            except (TypeError, ValueError) as error:
                raise ValueError("BAA data has invalid date or value.") from error
            if value <= 0:
                raise ValueError("BAA yield must be positive.")
            if available_on < observation_date:
                raise ValueError("BAA availability cannot precede its observation date.")
            if available_on < decision_date:
                rows.append({"observation_date": observation_date, "available_on": available_on, "value_percent": value, "source": raw["source"]})
    rows.sort(key=lambda row: row["observation_date"])
    if len(rows) < 2:
        raise ValueError("At least two point-in-time BAA observations are required for the signal.")
    return rows


def baa_signal(decision_date: date = SIGNAL_DECISION_DATE, window_observations: int | None = None) -> dict[str, Any]:
    rows = load_baa_asof(decision_date)
    if window_observations is not None:
        if window_observations < 2:
            raise ValueError("Signal window must contain at least two observations.")
        rows = rows[-window_observations:]
        if len(rows) < 2:
            raise ValueError("Signal window has fewer than two usable observations.")
    first, latest = rows[0], rows[-1]
    change_bps = round((latest["value_percent"] - first["value_percent"]) * 100, 1)
    return {
        "decision_date": decision_date.isoformat(),
        "first_observation": first["observation_date"].isoformat(),
        "latest_observation": latest["observation_date"].isoformat(),
        "first_yield_percent": first["value_percent"],
        "latest_yield_percent": latest["value_percent"],
        "change_bps": change_bps,
        "state": "credit-yield tightening" if change_bps > 0 else "credit-yield easing or unchanged",
    }


def constrained_portfolio(signal: dict[str, Any]) -> tuple[dict[str, float], str]:
    # Student judgment, not a source fact: when BAA rises, prefer A to D because
    # A has 14% Treasury/cash reserve and only 26% in the IG fund; D has 97% IG.
    if signal["change_bps"] > 0:
        return candidate_a(), "Candidate A selected after a positive BAA change; D remains an alternative coded-rule pass, not a suitability conclusion."
    return candidate_d(), "Candidate D selected only by the stated signal rule; it still needs a committee suitability judgment."


def issuer_weight(weights: dict[str, float], issuer: str) -> float:
    return sum(weights[name] for name, details in HOLDINGS.items() if not details["exempt"] and details["issuer"] == issuer)


def mandate_checks(weights: dict[str, float], prior_weights: dict[str, float] | None = None) -> dict[str, dict[str, str]]:
    validate_weights(weights)
    total = sum(weights.values())
    reserve = sum(weights[name] for name, details in HOLDINGS.items() if details["reserve"])
    liquid = sum(weights[name] for name, details in HOLDINGS.items() if details["days"] <= LIQUIDITY_DAYS)
    acme = issuer_weight(weights, "Acme Corp")
    if prior_weights is None:
        turnover = None
    else:
        validate_weights(prior_weights)
        turnover = 0.5 * sum(abs(weights[name] - prior_weights[name]) for name in UNIVERSE)
    return {
        "weights_sum": check(abs(total - 1.0) < 1e-9, f"{total:.1%}; mandate requires 100.0%."),
        "long_only": check(min(weights.values()) >= 0, f"Lowest weight is {min(weights.values()):.1%}; no short sales."),
        "reserve": check(reserve >= RESERVE_MINIMUM, f"{reserve:.1%} reserve-eligible versus {RESERVE_MINIMUM:.1%} required for four $0.75m distributions on $100m."),
        "liquidity": check(liquid >= LIQUIDITY_MINIMUM, f"{liquid:.1%} redeemable within {LIQUIDITY_DAYS} business days versus {LIQUIDITY_MINIMUM:.1%} required."),
        "issuer": check(acme <= ISSUER_MAXIMUM, f"Acme stock plus bonds = {acme:.1%}; maximum is {ISSUER_MAXIMUM:.1%}."),
        "derivatives": check(not any(weights[name] and HOLDINGS[name]["derivative"] for name in UNIVERSE), "All selected Lab 13 holdings are labeled non-derivative."),
        "borrowing": check(None, "Portfolio weights cannot establish whether the investor borrowed externally; committee evidence is required."),
        "turnover": check(None if turnover is None else turnover <= 0.25, "No prior approved portfolio was supplied." if turnover is None else f"{turnover:.1%}; limit is 25.0% without committee approval."),
        "calendar_year_loss": check(None, "S9 lacks a risk measure, test method, and breach procedure."),
    }


def proxy_weights(weights: dict[str, float]) -> tuple[dict[str, float] | None, list[str]]:
    result = {name: 0.0 for name in SLEEVES}
    unsupported = []
    for holding, weight in weights.items():
        if weight == 0:
            continue
        sleeve = RETURN_PROXY.get(holding, holding)
        if sleeve not in SLEEVES:
            unsupported.append(holding)
        else:
            result[sleeve] += weight
    return (None, unsupported) if unsupported else (result, [])


def expected_return_and_risk(weights: dict[str, float], expected_return_shift: float = 0.0) -> dict[str, Any]:
    proxied, unsupported = proxy_weights(weights)
    if proxied is None:
        return {"status": "NOT ASSESSED", "reason": "No course return/risk estimate for: " + ", ".join(unsupported) + ".", "gross_expected_return": None, "volatility": None}
    expected_return = sum(proxied[name] * (SLEEVES[name]["expected_return"] + expected_return_shift) for name in SLEEVES)
    variance = sum(
        proxied[left] * proxied[right] * CORRELATIONS[left][right] * SLEEVES[left]["volatility"] * SLEEVES[right]["volatility"]
        for left in SLEEVES for right in SLEEVES
    )
    return {"status": "PLANNING ESTIMATE", "reason": "Course planning inputs; Cash is proxied by Treasury bills. Net objective cannot be assessed because no cost input is supplied.", "gross_expected_return": round(expected_return, 6), "volatility": round(sqrt(variance), 6)}


def portfolio_record(name: str, weights: dict[str, float], prior_weights: dict[str, float] | None = None) -> dict[str, Any]:
    return {"name": name, "weights": weights, "mandate_checks": mandate_checks(weights, prior_weights), "planning_metrics": expected_return_and_risk(weights)}


def signal_data_card(signal: dict[str, Any]) -> dict[str, Any]:
    """Return display-ready, sourced signal metadata without UI-side calculation."""
    observations = load_baa_asof(SIGNAL_DECISION_DATE)
    return {
        "formula": "(latest usable BAA yield - earliest usable BAA yield) × 100 basis points",
        "provider": "FRED series BAA; source shown by FRED is Moody's. Historical information set: ALFRED vintage rule.",
        "units_frequency": "Percent, not seasonally adjusted; monthly.",
        "universe": "The eight Lab 13 holdings. The signal selects between existing Candidates A and D; it does not create securities.",
        "observations": [
            {"observation_date": row["observation_date"].isoformat(), "available_on": row["available_on"].isoformat(), "value_percent": row["value_percent"]}
            for row in observations
        ],
        "rebalance_timing": "Annual mandate rebalancing. The stored initial decision is 2026-10-02, the next decision day after the documented 2026-10-01 September release.",
        "transformations": "No imputation or forward fill. Values remain percentage points until the basis-point subtraction.",
        "missing_data_rule": "Stop if fewer than two usable observations exist, a date/value is invalid, a yield is nonpositive, or availability precedes observation date.",
        "lookahead_survivorship_risks": "Current FRED history may contain later observations or revisions; retrieve ALFRED at each future decision date. This macro series does not establish a survivorship-free security universe.",
        "costs": "No sourced trading-cost input exists; the net-of-cost objective is unscorable.",
        "model_result": f"{signal['change_bps']:.1f} bps: {signal['state']}.",
    }


def training_one_way_cost_bps() -> int:
    """Read the intact 10-bps Week 11 training input; it is not portfolio cost evidence."""
    if not TRAINING_COST_PATH.exists():
        raise FileNotFoundError(f"Missing transaction-cost training file: {TRAINING_COST_PATH}")
    with TRAINING_COST_PATH.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    if not rows or set(rows[0]) != {"period", "one_way_cost_bps", "source"}:
        raise ValueError("Transaction-cost training input has invalid columns.")
    try:
        values = {int(row["one_way_cost_bps"]) for row in rows}
    except (TypeError, ValueError) as error:
        raise ValueError("Transaction-cost training input has invalid values.") from error
    if values != {10}:
        raise ValueError("Course training input is not the documented uniform 10-bps value.")
    return values.pop()


def mandate_summary(record: dict[str, Any]) -> dict[str, list[str]]:
    """Group the engine's check statuses for a stress display; no new tests occur here."""
    result = {"PASS": [], "FAIL": [], "NOT TESTABLE": []}
    for rule, detail in record["mandate_checks"].items():
        result[detail["status"]].append(rule)
    return result


def stress_record(name: str, base: dict[str, Any], stressed: dict[str, Any], description: str, stop: dict[str, str] | None = None) -> dict[str, Any]:
    """Package calculated base/stress comparisons for the app without UI math."""
    return {
        "name": name,
        "description": description,
        "base": base,
        "stressed": stressed,
        "weight_change": {holding: round(stressed["weights"][holding] - base["weights"][holding], 8) for holding in UNIVERSE},
        "mandate_base": mandate_summary(base),
        "mandate_stressed": mandate_summary(stressed),
        "stop_condition": stop,
    }


def build_stress_output() -> dict[str, Any]:
    """Run bounded stresses using stated data and expose infeasible inputs visibly.

    These are not a changed-input record.  They do not overwrite the approved
    base configuration or claim that a training cost is a sourced portfolio cost.
    """
    base_signal = baa_signal()
    base_weights, _ = constrained_portfolio(base_signal)
    base = portfolio_record("Approved base constrained portfolio", base_weights)

    # Student stress assumption: lower every available course planning return by
    # 100 bps.  Volatility/correlation, weights, and mandate metadata are held.
    estimate_stressed = portfolio_record("Estimate stress", base_weights)
    estimate_stressed["planning_metrics"] = expected_return_and_risk(base_weights, expected_return_shift=-0.01)

    shorter_signal = baa_signal(window_observations=2)
    shorter_weights, shorter_reason = constrained_portfolio(shorter_signal)
    historical_stressed = portfolio_record("Shorter historical-window stress", shorter_weights)
    historical_stressed["signal"] = shorter_signal
    historical_stressed["selection_reason"] = shorter_reason

    # Week 11 supplies 10 bps one-way as a training signal cost.  It cannot be
    # converted to a portfolio dollar/return cost without sourced turnover.
    course_training_cost_bps = training_one_way_cost_bps()
    cost_stressed = portfolio_record("Transaction-cost stress", base_weights)
    cost_stressed["cost_assessment"] = {
        "input_one_way_bps": course_training_cost_bps,
        "source": "lessons/week-11/starter/signal_development.csv",
        "status": "INFEASIBLE",
        "reason": "The course input is a signal-development training cost, not a sourced portfolio trading cost; prior approved weights are also absent. No net-return deduction is calculated.",
    }

    constraint_stressed = portfolio_record("Constraint-completeness stress", base_weights)
    constraint_stop = {
        "status": "STOP",
        "condition": "Stop implementation whenever any mandatory mandate rule is FAIL or NOT TESTABLE.",
        "reason": "The mandate requires compliance before adoption. Current base output has NOT TESTABLE borrowing, turnover, and S9 calendar-year-loss checks; S4 and S10 remain unresolved committee decisions.",
    }
    return {
        "as_of": SIGNAL_DECISION_DATE.isoformat(),
        "base_configuration_preserved": True,
        "disclosure": "Stress runs are analysis scenarios, not the Locked Changed-Input Record. The approved base configuration remains unchanged.",
        "stop_condition": constraint_stop,
        "stresses": [
            stress_record(
                "Estimate downshift",
                base,
                estimate_stressed,
                "Student stress assumption: reduce each available course planning expected return by 100 bps. The course did not supply an alternate estimate set; this is a sensitivity assumption, not a sourced forecast.",
            ),
            stress_record(
                "Shorter historical window",
                base,
                historical_stressed,
                "Use the last two usable BAA observations (2026-08-01 and 2026-09-01) instead of all three. Both are available before the decision date.",
            ),
            stress_record(
                "Transaction-cost feasibility",
                base,
                cost_stressed,
                "Apply the course's 10-bps one-way training input as a feasibility probe only. The engine does not manufacture a net deduction without valid portfolio turnover and cost evidence.",
            ),
            stress_record(
                "Constraint completeness",
                base,
                constraint_stressed,
                "Require every mandatory mandate rule to be scorable as well as passing. This adds no invented numerical constraint.",
                constraint_stop,
            ),
        ],
    }


def build_output() -> dict[str, Any]:
    signal = baa_signal()
    constrained, selection_reason = constrained_portfolio(signal)
    records = [
        portfolio_record("Equal-weight baseline", equal_weight()),
        portfolio_record("60/40 comparison benchmark", benchmark_6040()),
        portfolio_record("Signal-selected constrained portfolio", constrained),
    ]
    benchmark_metrics = records[1]["planning_metrics"]
    constrained_metrics = records[2]["planning_metrics"]
    excess = None
    if benchmark_metrics["gross_expected_return"] is not None and constrained_metrics["gross_expected_return"] is not None:
        excess = round(constrained_metrics["gross_expected_return"] - benchmark_metrics["gross_expected_return"], 6)
    return {
        "as_of": SIGNAL_DECISION_DATE.isoformat(),
        "disclosures": {
            "ai_use": "AI was used to assist implementation and testing; the analysis and decision remain the student's responsibility.",
            "advice": "Education only, not investment advice.",
        },
        "source_facts": {"universe_source": "Lab 13 mandate.py", "return_risk_source": "course portfolio.py", "signal_source": "course BAA data card and documented observations"},
        "mandate_terms": {
            "source": "Lab 13 mandate S1 and S2 (lab-13.md).",
            "horizon": "Seven-year horizon.",
            "rebalance_frequency": "Annual rebalancing.",
            "return_objective": {
                "statement": "CPI + 4% net of costs over rolling five-year periods.",
                "status": "NOT TESTABLE",
                "reason": "No CPI series or sourced portfolio trading-cost input was supplied; the net-of-cost objective cannot be tested.",
            },
        },
        "student_judgments": {"benchmark_role": "Comparison benchmark only; not an allocation constraint.", "cash_proxy": "Cash is mapped to the course Treasury-bill planning estimate only for A's planning metrics.", "signal_rule": "If the as-of BAA change is positive, select Candidate A; otherwise select Candidate D."},
        "signal": signal,
        "signal_data_card": signal_data_card(signal),
        "selection_reason": selection_reason,
        "portfolios": records,
        "benchmark_comparison": {"constrained_minus_benchmark_gross_expected_return": excess, "interpretation": "Planning estimate only; no net-of-cost conclusion."},
        "scorability": {
            "costs": {"status": "NOT ASSESSED", "reason": "No sourced trading-cost input; CPI + 4% net-of-cost cannot be tested."},
            "turnover": {"status": "NOT TESTABLE", "reason": "No prior approved weights were supplied; annual turnover cannot be calculated."},
            "S4_benchmark_role": {"status": "UNRESOLVED", "reason": "The 60/40 mix is treated as a comparison benchmark. The CIO has not said whether it is the intended strategic allocation."},
            "S9_loss_limit": {"status": "UNRESOLVED", "reason": "No risk measure, test method, probability/window, or breach procedure was supplied."},
            "S10_optimization": {"status": "UNRESOLVED", "reason": "Optimization target and sector, ESG, tax, and home-bias preferences are missing."},
        },
        "limitations": ["No sourced costs: CPI + 4% net-of-cost objective is not assessed.", "S9 calendar-year loss and turnover cannot be fully tested from supplied inputs.", "No historical total-return series was supplied; this is not a backtest.", "Private real estate and Acme holdings lack course return/risk estimates, so equal-weight risk/return is not assessed."],
    }


def write_visible_output(path: Path = VISIBLE_OUTPUT_PATH) -> dict[str, Any]:
    output = build_output()
    path.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return output


def write_stress_output(path: Path = STRESS_OUTPUT_PATH) -> dict[str, Any]:
    output = build_stress_output()
    path.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return output


if __name__ == "__main__":
    write_visible_output()
    write_stress_output()
    print(f"Wrote {VISIBLE_OUTPUT_PATH}")
    print(f"Wrote {STRESS_OUTPUT_PATH}")
