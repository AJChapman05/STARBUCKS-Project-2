from datetime import date

import pytest

import analysis


def test_portfolio_weights_and_invalid_universe():
    assert sum(analysis.equal_weight().values()) == pytest.approx(1.0)
    with pytest.raises(ValueError, match="exactly the Lab 13 universe"):
        analysis.validate_weights({"invented ticker": 1.0})


def test_signal_timing_requires_next_decision_day():
    with pytest.raises(ValueError, match="At least two"):
        analysis.load_baa_asof(date(2026, 10, 1))
    signal = analysis.baa_signal(date(2026, 10, 2))
    assert signal["change_bps"] == pytest.approx(28.0)
    assert signal["latest_observation"] == "2026-09-01"


def test_returns_risk_and_benchmark_comparison():
    benchmark = analysis.expected_return_and_risk(analysis.benchmark_6040())
    assert benchmark["gross_expected_return"] == pytest.approx(0.068)
    assert benchmark["volatility"] > 0
    output = analysis.build_output()
    assert output["benchmark_comparison"]["constrained_minus_benchmark_gross_expected_return"] == pytest.approx(-0.0013)


def test_lab_13_mandate_terms_are_generated_and_objective_is_unscorable():
    terms = analysis.build_output()["mandate_terms"]
    assert terms["source"] == "Lab 13 mandate S1 and S2 (lab-13.md)."
    assert terms["horizon"] == "Seven-year horizon."
    assert terms["rebalance_frequency"] == "Annual rebalancing."
    assert terms["return_objective"]["statement"] == "CPI + 4% net of costs over rolling five-year periods."
    assert terms["return_objective"]["status"] == "NOT TESTABLE"
    assert "No CPI series" in terms["return_objective"]["reason"]


def test_equal_weight_has_no_invented_return_estimate():
    metrics = analysis.expected_return_and_risk(analysis.equal_weight())
    assert metrics["status"] == "NOT ASSESSED"
    assert "Private real estate fund" in metrics["reason"]


def test_liquidity_reserve_issuer_and_constraints():
    constrained = analysis.mandate_checks(analysis.candidate_a())
    assert constrained["reserve"]["status"] == "PASS"
    assert constrained["liquidity"]["status"] == "PASS"
    assert constrained["issuer"]["status"] == "PASS"
    assert constrained["long_only"]["status"] == "PASS"
    bad = analysis.equal_weight()
    checks = analysis.mandate_checks(bad)
    assert checks["liquidity"]["status"] == "FAIL"
    assert checks["issuer"]["status"] == "FAIL"


def test_acme_stock_and_bonds_are_aggregated():
    weights = {name: 0.0 for name in analysis.UNIVERSE}
    weights["Acme Corp bonds"] = 0.05
    weights["Acme Corp stock"] = 0.04
    weights["Cash"] = 0.91
    assert analysis.issuer_weight(weights, "Acme Corp") == pytest.approx(0.09)
    assert analysis.mandate_checks(weights)["issuer"]["status"] == "FAIL"


def test_turnover_and_missing_data_rules(monkeypatch, tmp_path):
    checks = analysis.mandate_checks(analysis.candidate_a())
    assert checks["turnover"]["status"] == "NOT TESTABLE"
    monkeypatch.setattr(analysis, "DATA_PATH", tmp_path / "missing.csv")
    with pytest.raises(FileNotFoundError):
        analysis.load_baa_asof(date(2026, 10, 2))


def test_invalid_signal_data_is_rejected(monkeypatch, tmp_path):
    bad_data = tmp_path / "baa.csv"
    bad_data.write_text(
        "observation_date,value_percent,available_on,source\n"
        "2026-07-01,not-a-number,2026-10-01,course card\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(analysis, "DATA_PATH", bad_data)
    with pytest.raises(ValueError, match="invalid date or value"):
        analysis.load_baa_asof(date(2026, 10, 2))


def test_stress_output_preserves_base_and_exposes_stop():
    stress = analysis.build_stress_output()
    assert stress["base_configuration_preserved"] is True
    assert stress["stop_condition"]["status"] == "STOP"
    assert [row["name"] for row in stress["stresses"]] == [
        "Estimate downshift",
        "Shorter historical window",
        "Transaction-cost feasibility",
        "Constraint completeness",
    ]
    estimate = stress["stresses"][0]
    assert estimate["stressed"]["planning_metrics"]["gross_expected_return"] == pytest.approx(0.0567)
    assert all(change == 0 for change in estimate["weight_change"].values())
    shorter = stress["stresses"][1]["stressed"]
    assert shorter["signal"]["change_bps"] == pytest.approx(15.0)
    costs = stress["stresses"][2]["stressed"]["cost_assessment"]
    assert analysis.training_one_way_cost_bps() == 10
    assert costs["status"] == "INFEASIBLE"
