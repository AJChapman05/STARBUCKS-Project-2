"""Render the frozen portfolio-analysis contract; calculate nothing here."""
from __future__ import annotations

import json
from pathlib import Path

import streamlit as st


OUTPUT = Path(__file__).parent / "visible_output.json"
STRESS_OUTPUT = Path(__file__).parent / "stress_output.json"


def percent(value):
    return "Not assessed" if value is None else f"{value:.2%}"


def show_status(status: str, message: str) -> None:
    """Present engine-provided statuses; this function makes no finance decision."""
    if status in {"FAIL", "STOP", "INFEASIBLE"}:
        st.error(message)
    elif status in {"NOT TESTABLE", "NOT ASSESSED", "UNRESOLVED"}:
        st.warning(message)
    else:
        st.success(message)


st.set_page_config(page_title="Meridian Portfolio Mandate", layout="wide")
st.title("Meridian Portfolio Mandate Engine")
st.caption("AI assisted implementation and testing; analysis and decision are the student's responsibility. Education only, not investment advice.")

if not OUTPUT.exists():
    st.error("Visible output is missing. Run `python analysis.py` before starting the app.")
    st.stop()
if not STRESS_OUTPUT.exists():
    st.error("Stress output is missing. Run `python analysis.py` before starting the app.")
    st.stop()

output = json.loads(OUTPUT.read_text(encoding="utf-8"))
stress_output = json.loads(STRESS_OUTPUT.read_text(encoding="utf-8"))
st.caption(f"Frozen engine output as of {output['as_of']}. The 60/40 portfolio is a comparison benchmark, not a hard allocation constraint.")

st.header("Decision status")
st.info(output["selection_reason"])
for item, detail in output["scorability"].items():
    show_status(detail["status"], f"{item.replace('_', ' ')} — {detail['status']}: {detail['reason']}")

st.header("Lab 13 mandate terms")
mandate_terms = output["mandate_terms"]
st.caption(f"Source: {mandate_terms['source']}")
st.write(f"**Horizon:** {mandate_terms['horizon']}")
st.write(f"**Rebalancing:** {mandate_terms['rebalance_frequency']}")
objective = mandate_terms["return_objective"]
show_status(objective["status"], f"Return objective — {objective['status']}: {objective['statement']} {objective['reason']}")

signal = output["signal"]
st.header("Point-in-time signal")
st.write(f"BAA moved {signal['change_bps']:.1f} bps from {signal['first_observation']} to {signal['latest_observation']}; the decision date is {signal['decision_date']}.")
with st.expander("Signal data card", expanded=True):
    card = output["signal_data_card"]
    st.write(f"**Formula:** {card['formula']}")
    st.write(f"**Source/provider:** {card['provider']}")
    st.write(f"**Units/frequency:** {card['units_frequency']}")
    st.write(f"**Universe:** {card['universe']}")
    st.dataframe(
        [{"Observation date": row["observation_date"], "Available on": row["available_on"], "BAA yield (%)": row["value_percent"]} for row in card["observations"]],
        hide_index=True,
        use_container_width=True,
    )
    for label in ("rebalance_timing", "transformations", "missing_data_rule", "lookahead_survivorship_risks", "costs", "model_result"):
        st.write(f"**{label.replace('_', ' ').title()}:** {card[label]}")

st.header("Portfolios and mandate verdicts")
for record in output["portfolios"]:
    st.subheader(record["name"])
    left, right = st.columns((1, 1))
    with left:
        st.caption("Weights")
        st.dataframe(
            [{"Holding": name, "Weight": percent(value)} for name, value in record["weights"].items() if value],
            hide_index=True,
            use_container_width=True,
        )
    with right:
        metrics = record["planning_metrics"]
        st.caption("Return and risk")
        st.metric("Gross expected return", percent(metrics["gross_expected_return"]))
        st.metric("Volatility", percent(metrics["volatility"]))
        show_status(metrics["status"], f"Risk/return — {metrics['status']}: {metrics['reason']}")
    checks = [{"Rule": rule.replace("_", " ").title(), "Status": detail["status"], "Reason": detail["reason"]} for rule, detail in record["mandate_checks"].items()]
    st.dataframe(checks, hide_index=True, use_container_width=True)
    for check_row in checks:
        if check_row["Status"] != "PASS":
            show_status(check_row["Status"], f"{record['name']} — {check_row['Rule']}: {check_row['Reason']}")

st.header("Benchmark comparison")
comparison = output["benchmark_comparison"]
st.metric("Constrained minus 60/40 gross expected return", percent(comparison["constrained_minus_benchmark_gross_expected_return"]))
st.caption(comparison["interpretation"])

st.header("Engine limitations")
for item in output["limitations"]:
    st.warning(item)

st.header("Required stress analysis")
st.caption(stress_output["disclosure"])
process_stop = stress_output["stop_condition"]
show_status(process_stop["status"], f"Process stop condition — {process_stop['condition']} {process_stop['reason']}")

for stress in stress_output["stresses"]:
    with st.expander(stress["name"], expanded=True):
        st.write(stress["description"])
        base_metrics = stress["base"]["planning_metrics"]
        stressed_metrics = stress["stressed"]["planning_metrics"]
        st.dataframe(
            [
                {"Measure": "Gross expected return", "Base": percent(base_metrics["gross_expected_return"]), "Stress": percent(stressed_metrics["gross_expected_return"])},
                {"Measure": "Volatility", "Base": percent(base_metrics["volatility"]), "Stress": percent(stressed_metrics["volatility"])},
                {"Measure": "Risk/return status", "Base": base_metrics["status"], "Stress": stressed_metrics["status"]},
            ],
            hide_index=True,
            use_container_width=True,
        )
        st.dataframe(
            [{"Holding": holding, "Weight change": percent(change)} for holding, change in stress["weight_change"].items()],
            hide_index=True,
            use_container_width=True,
        )
        st.write(f"**Mandate pass/fail, base:** {stress['mandate_base']}")
        st.write(f"**Mandate pass/fail, stress:** {stress['mandate_stressed']}")
        assessment = stress["stressed"].get("cost_assessment")
        if assessment:
            show_status(assessment["status"], f"Transaction costs — {assessment['status']}: {assessment['reason']} Input: {assessment['input_one_way_bps']} bps one way from {assessment['source']}.")
        if stress["stop_condition"]:
            show_status(stress["stop_condition"]["status"], f"Stress outcome — {stress['stop_condition']['condition']} {stress['stop_condition']['reason']}")
