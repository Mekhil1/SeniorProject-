# BearPilot student services

One Flask application serves Academic Advising, CS Tutoring, Career, and Student
Success. All browser requests go to the same local server. Credentials stay on
the server; do not put keys in HTML, JavaScript, commits, screenshots, or chats.

## Windows quick start

Use Python 3.11 or newer (3.12 recommended), Git, and PowerShell. In the VS Code
terminal, from the repository root:

```powershell
.\setup.ps1
code .env
```

Setup creates `.venv`, installs the shared dependencies, checks for conflicts,
copies `.env.example` if needed, and generates a local session secret. It does
not overwrite existing keys, configure IAM, deploy agents, or call models.
Enter authorized keys privately into `.env`, save, and run:

```powershell
.\start.ps1
```

Open <http://127.0.0.1:5001>, sign up with a Morgan email and a password of at
least 12 characters, then sign in and select a service card. Accounts live in
this checkout's ignored `instance/` directory; accounts from another laptop or
drive are not copied by Git. A Degree Works PDF is optional at signup.

If PowerShell blocks scripts, use these equivalent commands without changing
machine execution policy:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe scripts/configure_local.py
.\.venv\Scripts\python.exe app.py
```

On macOS/Linux use `python3 -m venv .venv` and `.venv/bin/python` for the Python
commands above. The PowerShell launchers are optional conveniences.

## Credentials: shared setup, different provider contracts

| Service | Credential | Runtime |
| --- | --- | --- |
| Academic Advising | `ADVISING_API_KEY` | Direct Gemini; curriculum database first |
| Tutoring | ADC when its engine ID is set, otherwise `TUTORING_API_KEY` | Existing deployed agent or local specialist + QA |
| Student Success | ADC when its engine ID is set, otherwise `SUCCESS_API_KEY` | Existing deployed agent or local ADK |
| Career | Google Application Default Credentials (ADC) | Existing deployed Agent Engine |

Enter each teammate's key in its named field. Advising uses its separate Cloud
project; Tutoring and Success keep separate keys even though they belong to the
same Cloud project. A missing key disables only that agent: the application never
borrows another agent's key or silently changes projects. Generic
`GEMINI_API_KEY` and `GOOGLE_API_KEY` variables are not used for authentication.
When migrating an old .env, copy each existing key into its correct named field
locally; setup does not guess ownership or move credentials automatically.

Models, restrictions, permissions, billing and quota belong to the project behind
each key. Two keys in the same project can still share project-level quota.
API-key mode is explicitly selected so an unrelated global Vertex flag does not
redirect these requests. A valid key for one model does not establish access to
every model; verify each agent with its own key before a presentation.

Existing model defaults are unchanged: Advising `gemini-2.5-flash`, Tutoring
`gemini-3.1-flash-lite`, Success `gemini-3.5-flash`. If your approved key/project
uses another supported model, set `ADVISING_MODEL`, `TUTORING_MODEL`, or
`SUCCESS_MODEL` explicitly and restart the server. Legacy `GEMINI_MODEL` remains
an Advising fallback. Model overrides do not change prompts or routing.

Tutoring and Success now also support their existing deployed ADK agents through
ADC. The example selects these deployments in `cosc-490`, `us-west1`:

| Service | Engine setting | Existing engine ID |
| --- | --- | --- |
| Tutoring | `TUTORING_REASONING_ENGINE_ID` | `4882328606581194752` |
| Success | `SUCCESS_REASONING_ENGINE_ID` | `3125784014418345984` |

When an engine ID is set, that service calls the deployed runtime using ADC.
`TUTORING_RUNTIME_PROJECT` / `TUTORING_RUNTIME_LOCATION` and the corresponding
`SUCCESS_RUNTIME_*` settings select its project and region independently.
The server identity needs permission to create/query sessions on each engine.
Use `gcloud auth application-default login` for local user credentials.
Restart Flask after changing environment settings.

Clear a service's engine ID to use its existing local API-key implementation.
Local Tutoring and Success answer independent questions. Runtime mode reuses
managed sessions through `tutoring_session_id` and `success_session_id` in each
browser tab. New chat clears only that service's conversation ID. Browser
`user_id` values distinguish clients and do not provide authentication.
Success's local ADK mode can alternatively use Vertex with
`SUCCESS_USE_VERTEXAI=true` and ADC when no Success API key is present.

### Career's endpoint is not an API key

The example environment explicitly selects development RC2
`6244403611070103552`, project `cosc-490`, region `us-west1`. The existing code's
production fallback is unchanged. Do not clear the development override or
deploy/update/delete an engine while configuring local development.

Career needs a Google identity authorized to create/query sessions on the
configured engine. For local user credentials, install the Google Cloud CLI and
run this yourself:

```powershell
gcloud auth application-default login
gcloud auth application-default set-quota-project cosc-490
```

`gcloud auth login` alone is different from application-default login. The quota
project command may also require permission. Ask the project owner for approved
access if you get a permission error; setup never grants roles automatically.
An approved private service-account credential file can instead be referenced
by an absolute `GOOGLE_APPLICATION_CREDENTIALS` path. Never copy that JSON into
Git or distribute a personal credential/token as a shared team key.

For teammates without cloud access, a centrally hosted backend with an approved
runtime identity is another option; hosting and access control are separate
tasks. Putting the endpoint or a Gemini key in the frontend does not grant ADC
permissions. The current local server listens on loopback, so each teammate
starts their own copy; it is not exposed to other laptops or the internet.

## Diagnose a service before a demonstration

```powershell
.\.venv\Scripts\python.exe scripts/check_setup.py
```

This reports missing packages, keys, the session secret, local ADC availability,
and engine-ID format without printing secrets or making model/network requests.
`OK` means local configuration exists, not that the provider has accepted it.
An unconfigured agent does not prevent the rest of the application starting.
Restart Flask after changing `.env`; existing process variables take precedence.

- Startup import error: run setup and install the full root requirements, not
  only a teammate's nested agent requirements.
- Advising HTTP 401/403: sign in through the app; its UI obtains CSRF tokens.
- A service says not configured: check its named API key locally.
- Career authentication/access error: check ADC and the configured project's
  IAM permissions. Changing a Gemini key will not repair Career authentication.
- HTTP 429/503: inspect the configuration check and server logs; provider quota
  or capacity may be exhausted. Do not repeatedly click Retry during a 429.
- Academic curriculum answers can work without a key; broader AI answers need
  Gemini. Uploaded student records remain on the existing local parsing path.

## Tests

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m pytest -q tests/test_configuration.py tests/test_api.py tests/test_agents.py tests/test_career_config.py
```

The configuration/integration tests use synthetic credentials and mocked model
responses. They do not establish live model availability. The repository also
contains historical Career optimization manifests under `tests/diagnostics`;
their byte-level assertions predate later team merges and can fail on intentional
changes or checkout line endings. Do not erase those records, revert teammates'
work, or weaken Career prompt/evidence checks to make a setup check green.
