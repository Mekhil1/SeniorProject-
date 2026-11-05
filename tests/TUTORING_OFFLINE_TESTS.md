# Offline tutoring and shared-hub checks

Never supply real Gemini/Google credentials to these checks. Historical credential safety remains unresolved. Tests use synthetic values, mock providers and block external browser traffic/model authentication.

## Existing local environments

From the repository root, the validated environments are:

- `.venv-step3/upgrade-step5/Scripts/python.exe`: Python 3.12.14, approved application dependencies and pytest/Ruff.
- `.venv-step3/Scripts/python.exe`: the earlier isolated Python 3.12 browser-test environment, also with the approved Google SDK versions and Playwright **1.64.1**.
- Installed Chrome: `C:\Program Files\Google\Chrome\Application\chrome.exe`.
- Node **24.22.1** was used for the dependency-free `.cjs` checks.

These local virtualenvs are not repository deliverables. A reviewer must provision a separate test environment with the approved combined manifests and pytest, plus optional test-only `playwright==1.64.1`. Do not install browser tooling into a teammate's environment or add it as an application runtime dependency. Browser paths and the Git path in `run_offline.py` currently target Windows; portable CI provisioning remains a separate reviewed task.

## Browser library fixtures

The browser tests serve these real library files from `.venv-step3/browser-assets/` and abort all other external asset requests:

| Local file | Public source | Expected SHA-256 |
|---|---|---|
| `marked.js` | `https://cdn.jsdelivr.net/npm/marked@16.4.1/lib/marked.umd.js` | `aced561246e2cf95f6a7007310a73c2edfc86e2ee136ae0c11a59f9ac8fee097` |
| `purify.js` | `https://cdn.jsdelivr.net/npm/dompurify@3.2.6/dist/purify.min.js` | `89e1fa7647cb495370d3a997ace4387f5d15d9f4c5af12352c53daa400956287` |

A reviewer may download these public files once during an approved setup step and verify them with `Get-FileHash -Algorithm SHA256`. The tests themselves do not fetch libraries, models or Cloud resources. Existing Career unversioned CDN paths are mapped to these known compatible fixtures for the offline test; actual remote CDN version availability is not certified. Do not commit a virtualenv/cache merely to supply fixtures.

## Commands

Use the intended isolated interpreter explicitly. Keep TEMP/TMP in a private test directory if Windows sandbox temp access is restricted.

```powershell
node tests/shared_hub_frontend.cjs
node tests/tutoring_frontend.cjs
& .\.venv-step3\Scripts\python.exe -B tests/tutoring_e2e.py --legacy-regression
& .\.venv-step3\Scripts\python.exe -B tests/tutoring_e2e.py
& .\.venv-step3\Scripts\python.exe -B tests/tutoring_browser.py

& .\.venv-step3\upgrade-step5\Scripts\python.exe -B tests/run_offline.py tests/test_agents.py tests/test_api.py tests/test_career_config.py tests/test_career_evidence.py tests/test_tutoring.py tests/test_tutoring_reliability.py tests/test_dependency_compatibility.py tests/test_tutoring_integration.py -q --tb=short -p no:cacheprovider
& .\.venv-step3\upgrade-step5\Scripts\python.exe -B tests/run_offline.py tests -q --tb=short -p no:cacheprovider
```

If Node is not on PATH, use the locally installed Node executable. The first browser command is a persistent regression for the old `ask`/`openAgent` misrouting. The second runs the real shared Flask application on a temporary loopback port, exercising actual tutoring service/coordinator/specialist/QA functions with mocked SDK responses. It also checks all three teammate pages/endpoints and error/retry contracts. The final browser command isolates UI rendering/error cases with fulfilled API responses; it is not the proof of server integration.

Full-suite historical integrity failures remain gates, not waived tests. Any approved shared-hub byte transition must be reviewed by Career's checksum owner; do not update expected hashes automatically.
