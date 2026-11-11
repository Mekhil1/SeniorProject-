# Tutoring dependency ownership

Tutoring directly requires Flask, python-dotenv, google-genai and httpx. Exact tested runtime versions are in this directory's `requirements.txt`. Python 3.12.14 was tested. These pins are a proposed module-owned baseline; they do not change the root installation automatically.

## Isolated module installation

From the repository root, create a new environment, without reusing an existing team environment:

```powershell
py -3.12 -m venv .venv/tutoring-review
& .\.venv\tutoring-review\Scripts\python.exe -m pip install -r agents/tutoring/requirements.txt
& .\.venv\tutoring-review\Scripts\python.exe -m pip check
```

Choose another new path if that environment already exists. The `.venv/` directory is already ignored by this repository. No environment creation or installation into that example path was performed as part of this review.

The manifest covers the tutoring modules and blueprint, not the entire application factory. Running the team's `app.py` additionally requires root application dependencies, including Flask-Cors and the other agents' dependencies. Installing this manifest does not create a standalone server, install a production WSGI server, or deploy a service.

ADK and AI Platform are not direct Tutoring dependencies. Google authentication, requests and other packages may still be installed transitively by the Gen AI SDK; that is different from Tutoring importing them directly. Pytest is a test dependency, not a runtime requirement.

## Shared application installation

After team approval of a compatible ADK choice, install the root and module manifests **in the same pip invocation in a fresh environment**:

```powershell
python -m pip install -r requirements.txt -r agents/tutoring/requirements.txt
python -m pip check
```

Use the intended environment's Python executable. Avoid installing the files sequentially and ignoring dependency errors. Root requirements do not automatically include nested requirement files. No root include was added.

This module now pins Gen AI **2.34.0**, coordinated with the root manifest's Gen AI **2.34.0**, HTTPX **0.28.1**, ADK **2.12.0** and AI Platform **1.165.1** pins. The former module SDK pin was 1.75.0; it fit the former root `<2` range but conflicted with Career's ADK 2.12.0. The coordinated upgrade removes that declared conflict without changing Career's manifest or service logic.

Career already pins ADK 2.12.0 and AI Platform 1.165.1. To validate the same set of manifests together, include `-r agents/career/workflow/requirements.txt` in the installation command above. Those requirements overlap consistently; do not upgrade or downgrade their versions independently. Changes remain local proposals pending review, not authorization to deploy or call live models.

Use Python **3.12.x** for the validated shared environment. Gen AI 2.34.0 and ADK 2.12.0 require Python >=3.11; older Python versions supported by the previous SDK are no longer sufficient for this set. Package metadata permission for other Python versions does not substitute for testing.

## Configuration and deployment

Tutoring uses the direct Gemini API. Runtime obtains its dedicated `TUTORING_API_KEY` from the process environment or the project-root `.env` loaded at application startup. It does not reuse Advising's or Success's key; no key belongs in requirements, source, reports or Git. Dependency installation and imports do not require a real key. Tests use mocks and synthetic values; live calls require separate authorization.

For the existing shared Flask deployment, incorporate this manifest in the environment-build step after compatibility approval, then run offline tests and `pip check`. Do not execute model smoke scripts while building/installing. No change to a teammate's deployed agent runtime is implied.

See `TUTORING_DEPENDENCY_ISOLATION_REPORT.md` at the repository root for evidence, known constraints and the test environment used in this review. A separate tutoring service is not necessary for the tested shared-compatible stack; it is an architectural fallback only if the team deliberately retains mutually incompatible SDK versions.
