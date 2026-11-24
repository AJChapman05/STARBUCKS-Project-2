Fresh README verification (project-local clean environment)
Timestamp observed: 2026-11-23 20:40:49 MST
Working directory: /Users/ajchapman/ai-finance-fin43900/project-2-investment-management

Fresh-environment commands:
  python3 -m venv --clear .venv
  .venv/bin/python -m pip install -r requirements.txt
  .venv/bin/python analysis.py
  .venv/bin/python -m pytest -q
  .venv/bin/python -m json.tool visible_output.json
  .venv/bin/python -m json.tool stress_output.json
  .venv/bin/streamlit run app.py --server.headless true --server.port 8521 --browser.gatherUsageStats false

Initial observed test result before the test-only correction:
  9 passed, 1 failed
  Failed test: tests/test_app.py::test_app_renders_engine_results_and_warnings
  Cause reported: Streamlit AppTest .run(timeout=10) timed out in a clean first-run environment.

Correction and scope:
  tests/test_app.py was changed only from run(timeout=10) to run(timeout=30).
  No financial model, source data, holding, return assumption, constraint, stress input,
  or recommendation was changed.

Rerun observed result:
  analysis.py wrote visible_output.json and stress_output.json.
  10 passed in 0.67s
  Both regenerated JSON files parsed successfully with python -m json.tool.
  Streamlit started headlessly and printed Local URL: http://localhost:8521
  Startup also printed an urllib3 LibreSSL warning; it did not prevent startup.

Interpretation boundary:
  localhost:8521 was a temporary local process endpoint, not a deployed application or
  GitHub publication. The outputs remain subject to the unresolved mandate limitations
  documented in README.md and docs/validation-and-ai-use.md.
