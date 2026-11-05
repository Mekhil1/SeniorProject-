# Four-agent local setup and offline validation

Use a new Python 3.12 environment. Do not transfer dotenv files, databases, credentials, virtual environments or caches from another machine. This integration candidate has not been published to GitHub.

From the application root on Windows:

```powershell
py -3.12 -m venv .venv
& .\.venv\Scripts\python.exe -m pip install --isolated --index-url https://pypi.org/simple -r requirements.txt -r agents/tutoring/requirements.txt -r agents/career/workflow/requirements.txt -r requirements-dev.txt playwright==1.64.1
& .\.venv\Scripts\python.exe -m pip check
# New fixture database only: do not run against an existing database to preserve.
& .\.venv\Scripts\python.exe -B scripts/seed_database.py
& .\.venv\Scripts\python.exe -B tests/run_offline.py
node tests/shared_hub_frontend.cjs
node tests/tutoring_frontend.cjs
& .\.venv\Scripts\python.exe -B tests/tutoring_e2e.py
```

`requirements-dev.txt` supplies the existing pytest>=8,<9 policy. Do not install an unconstrained pytest afterward. Runtime Google pins remain Gen AI 2.34.0, ADK 2.12.0, AI Platform 1.165.1 and HTTPX 0.28.1. Requirements with ranges are not a complete cross-platform hash lock. Never ignore a download hash failure: independently verify the artifact against its authoritative PyPI release metadata before retrying.

Browser tests need installed Windows Chrome and Node. See tests/TUTORING_OFFLINE_TESTS.md for exact paths and two public JavaScript fixture hashes. Provision only marked@16.4.1 and DOMPurify@3.2.6 under .venv-step3/browser-assets, verify those documented hashes, and keep that fixture directory out of Git. It is not a Python environment. The browser test starts and stops a real local Flask server, fulfills public library requests from local fixtures, mocks external providers and blocks other network requests. It tests the actual Tutoring coordinator/specialist/QA pipeline.

For a local website after safe test configuration, use the intended environment to run `python -m flask --app advisor:create_app run --host 127.0.0.1`, then open http://127.0.0.1:5000/chat. This command alone does not mock provider calls. Use the browser integration test for credential-free functional testing; no real credentials or provider questions are authorized by these setup instructions.

All four agent pages share Flask: academic -> /api/adviser, career -> /api/career, success -> /api/success and tutoring -> /api/tutoring. Student Success retains the current main 503 error contract. Tutoring remains stateless; browser prototype account controls are not production authentication.

Career integrity/history checks must remain enabled. This source-only review candidate lacks the genuine historical Git checkpoint; owner-approved safe history preparation and precise integrity transitions remain required. Do not normalize protected files, edit historical evidence, skip checks or invent Git history to get a passing suite. Do not publish or use live providers until the separately documented approvals/security gates are cleared.
