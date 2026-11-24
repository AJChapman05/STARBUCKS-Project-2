from pathlib import Path

from streamlit.testing.v1 import AppTest

import analysis


def test_app_renders_engine_results_and_warnings():
    analysis.write_visible_output()
    app_path = Path(__file__).parents[1] / "app.py"
    # A clean first-run Streamlit environment can exceed AppTest's 3-second
    # default while loading dependencies; this is a UI-test timeout only.
    tested = AppTest.from_file(str(app_path)).run(timeout=30)

    assert not tested.exception
    assert tested.title[0].value == "Meridian Portfolio Mandate Engine"
    rendered = " ".join(item.value for item in tested.markdown) + " ".join(item.value for item in tested.info)
    assert "Candidate A selected" in rendered
    assert "Seven-year horizon" in rendered
    assert "Annual rebalancing" in rendered
    warnings = " ".join(item.value for item in tested.warning)
    assert "CPI + 4% net of costs over rolling five-year periods" in warnings
    assert "Return objective — NOT TESTABLE" in warnings
    assert "S4 benchmark role" in warnings
    assert "S9 loss limit" in warnings
    assert "S10 optimization" in warnings
    assert "Equal-weight baseline — Liquidity" in " ".join(item.value for item in tested.error)
