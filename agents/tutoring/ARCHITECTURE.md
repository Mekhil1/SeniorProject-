# Tutoring integration boundary

Follow the team's Flask blueprint -> service -> agent/provider boundary. The service owns coordinator -> subject specialist -> QA; the route owns validation, HTTP status and the final JSON contract. Do not call provider SDKs from browser code or shared navigation.

POST /api/tutoring accepts a JSON object with a nonempty question up to 8,000 characters. Success is {"reply": "...", "implemented": true}; errors use {"error": "..."} with an appropriate non-2xx status. The frontend uses the same-origin endpoint and sanitizes Markdown output before display. Preserve its duplicate guard, abort/timeout and recovery behavior.

Career uses the same application boundary but carries user_id/session_id through its deployed runtime adapter. Tutoring is intentionally stateless. Do not invent Career-style session identifiers without persistent conversation semantics. Career's ADK workflow and deployment packaging are agent-specific, not a mandatory framework for all services. Tutoring directly requires Flask, dotenv, Gen AI and HTTPX; install its manifest together with root/Career manifests for the shared application.

Keep bounded provider calls, missing-configuration checks and fixed safe errors. Do not copy Career prompts, workflow tools, credential clients, evidence adapters or checksum fixtures. Stage timing without request/provider content is a useful future observability option, not a required architectural rewrite.

Tests should mock providers at their boundary and retain the real coordinator/specialist/QA path for integration checks. Shared page/API contracts, Student Success's current 503 response, Academic advising and Career session behavior must remain unchanged.

Career source, historical evidence, checksum allowlists and integrity tests are immutable under the current owner direction. Existing baseline EOL/history failures and shared-file compatibility gates are not resolved by changing Tutoring frameworks. Preserve the necessary hub redirect and early-return guard; if team integration requires protected shared changes, request a separate team-owned policy decision without suppressing or rewriting historical assertions.
