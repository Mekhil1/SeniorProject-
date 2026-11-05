"""Real loopback Flask + Chrome integration; only providers/CDN assets are mocked.

Run with the existing isolated browser-test interpreter. Never calls Google.
"""
import os
import socket
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

from playwright.sync_api import sync_playwright
from werkzeug.serving import make_server

ROOT = Path(__file__).resolve().parents[1]
os.chdir(ROOT)
import sys

sys.path.insert(0, str(ROOT))
CONNECT = socket.socket.connect


def loopback_only(sock, address):
    if isinstance(address, tuple) and address[0] in ("127.0.0.1", "::1", "localhost"):
        return CONNECT(sock, address)
    raise AssertionError("External sockets forbidden")


def forbidden(*args, **kwargs):
    raise AssertionError("Real model/authentication forbidden")


def run(legacy_only=False):
    for name in ["GEMINI_API_KEY", "GOOGLE_API_KEY", "GOOGLE_APPLICATION_CREDENTIALS", "GOOGLE_GEMINI_BASE_URL", "GOOGLE_GENAI_USE_VERTEXAI"]:
        os.environ.pop(name, None)
    os.environ["GEMINI_API_KEY"] = "offline-placeholder"
    state = {"mode": "ok"}
    trace, payloads, api_requests = [], [], []
    lock = threading.Lock()
    with patch("dotenv.load_dotenv", lambda *a, **k: None), patch("socket.socket.connect", loopback_only), patch("google.auth.default", forbidden):
        from advisor import create_app
        from agents.tutoring import quality_assurance, specialists

        def generate(*, contents, config, **kwargs):
            qa = config.system_instruction == quality_assurance.QA_INSTRUCTIONS
            question = contents.split("STUDENT QUESTION:\n", 1)[1].split("\n\nSPECIALIST RESPONSE:", 1)[0] if qa else contents
            with lock:
                trace.append({"stage": "qa" if qa else "specialist", "question": question,
                              "algorithm_prompt": "algorithms and data structures tutor" in config.system_instruction})
            time.sleep(2 if "cancel navigation" in question else 0.12)
            if state["mode"] == "qa_failure" and qa:
                raise RuntimeError("Synthetic provider diagnostic")
            if not qa:
                return SimpleNamespace(text="Draft for " + question)
            assert "Draft for " + question in contents
            return SimpleNamespace(text="## Reviewed lesson\n1. " + question + "\n2. Try a practice example.\n```python\nx = 1\n```\n<img src=x onerror='window.pwned=1'>\n[bad](javascript:alert(1))")

        def client_factory(**kwargs):
            assert kwargs["api_key"] == "offline-placeholder"
            assert kwargs["vertexai"] is False
            client = Mock()
            client.models.generate_content.side_effect = generate
            return client

        def career_reply(**kwargs):
            if state["mode"] == "career_failure":
                raise RuntimeError("Synthetic provider diagnostic")
            return {"reply": "Career offline reply", "session_id": "offline-session", "user_id": kwargs["user_id"]}

        with patch("google.genai.Client", side_effect=client_factory), patch("agents.career.routes.answer", side_effect=career_reply), patch("agents.success.routes.answer", side_effect=lambda question: None if state["mode"] == "success_failure" else "Success offline reply"), patch("advisor.routes.answer_from_database", return_value=None), patch("advisor.routes.answer_with_ai", return_value="Academic offline reply"):
            app = create_app({"TESTING": True})
            # Imported modules have already captured the patched no-op dotenv loader.
            assert specialists.load_dotenv is quality_assurance.load_dotenv
            app.config["PROPAGATE_EXCEPTIONS"] = False
            server = make_server("127.0.0.1", 0, app, threaded=True)
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            base = f"http://127.0.0.1:{server.server_port}"
            try:
                with sync_playwright() as pw:
                    browser = pw.chromium.launch(executable_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe", headless=True)
                    context = browser.new_context()

                    def gate(route):
                        url = route.request.url
                        if url.startswith(base + "/"):
                            if "/api/" in url:
                                api_requests.append((route.request.method, url.removeprefix(base)))
                            if url.endswith("/api/tutoring"):
                                payload = route.request.post_data_json
                                assert set(payload) == {"question"}
                                payloads.append(payload)
                            route.continue_()
                        elif "/npm/marked@16.4.1/" in url or "/npm/dompurify@3.2.6/" in url or "/npm/marked/" in url or "/npm/dompurify/" in url:
                            file = "marked.js" if "/npm/marked" in url else "purify.js"
                            route.fulfill(body=(ROOT / ".venv-step3/browser-assets" / file).read_text(encoding="utf-8"), content_type="application/javascript")
                        else:
                            route.abort()

                    context.route("**/*", gate)
                    page = context.new_page()
                    assert page.request.get(base + "/api/health").json()["status"] == "ok"
                    page.goto(base + "/")
                    assert page.locator("#loginForm").count() == 1
                    # Existing prototype login uses browser records, not server authentication.
                    page.evaluate("localStorage.setItem('msu_user_offline@morgan.edu', JSON.stringify({name:'Offline student',email:'offline@morgan.edu'}))")
                    page.locator("#email").fill("offline@morgan.edu")
                    page.locator("#password").fill("synthetic-only")
                    page.get_by_role("button", name="Sign In", exact=True).click()
                    page.wait_for_url(base + "/chat")
                    if legacy_only:
                        page.evaluate("ask('CS topic: binary search in Python')")
                        page.wait_for_timeout(250)
                        assert not any(path == "/api/adviser" for method, path in api_requests), "Legacy Tutoring selection posted to /api/adviser"
                        page.wait_for_url(base + "/agents/tutoring", timeout=5000)
                        page.get_by_role("link", name="Student Hub").click()
                        page.evaluate("openAgent('CS Learning & Tutoring')")
                        page.wait_for_url(base + "/agents/tutoring", timeout=5000)
                        assert not any(path == "/api/adviser" for method, path in api_requests)
                        page.get_by_role("link", name="Student Hub").click()
                        page.wait_for_url(base + "/chat")
                        page.wait_for_function("typeof ask === 'function'")
                        page.evaluate("ask('Plan my courses')")
                        page.get_by_text("Academic offline reply", exact=True).wait_for()
                        assert [path for method, path in api_requests if method == "POST"] == ["/api/adviser"]
                        browser.close()
                        print("PASS: legacy ask/openAgent Tutoring navigation, no unexpected advising API request")
                        return
                    page.get_by_role("button", name="Explore learning support").click()
                    page.wait_for_url(base + "/agents/tutoring")
                    page.locator("#send").click()
                    assert not payloads
                    page.locator("#question").fill("Explain binary search in Python")
                    page.evaluate("document.getElementById('form').requestSubmit(); requestAnswer('duplicate');")
                    page.locator("[aria-busy=true]").wait_for()
                    assert page.locator("#send").is_disabled()
                    page.locator(".msg.bot pre code").wait_for()
                    assert len(payloads) == 1
                    assert page.locator(".msg").count() == 3  # welcome + user + one response
                    assert [t["stage"] for t in trace] == ["specialist", "qa"]
                    assert trace[0]["algorithm_prompt"]
                    assert page.locator(".msg.bot h2").inner_text() == "Reviewed lesson"
                    assert page.locator(".msg.bot [onerror], .msg.bot a[href^='javascript:']").count() == 0
                    assert page.evaluate("window.pwned || 0") == 0
                    assert page.get_by_role("button", name="Copy", exact=True).count() == 1

                    # Real Flask validation, not a fulfilled browser API route.
                    for data, content_type in [("{", "application/json"), ('["bad"]', "application/json"), ('{"question":false}', "application/json")]:
                        assert page.request.post(base + "/api/tutoring", data=data, headers={"Content-Type": content_type}).status == 400
                    assert page.request.post(base + "/api/tutoring", data={"question": "x" * 8001}).status == 413
                    assert page.request.get(base + "/api/tutoring").status == 405
                    state["mode"] = "qa_failure"
                    page.locator("#question").fill("SQL joins")
                    page.locator("#send").click()
                    page.get_by_role("button", name="Retry", exact=True).wait_for()
                    assert "Synthetic provider diagnostic" not in page.locator("#messages").inner_text()
                    state["mode"] = "ok"
                    page.get_by_role("button", name="Retry", exact=True).click()
                    page.wait_for_function("!document.querySelector('.msg.error') && !document.getElementById('send').disabled")

                    # Browser-only error cases stay distinct from the real pipeline proof above.
                    def broken(route):
                        route.fulfill(status=502, body="not JSON", content_type="text/html")
                    page.route("**/api/tutoring", broken)
                    page.locator("#question").fill("Malformed response")
                    page.locator("#send").click()
                    page.get_by_text("The server returned an unreadable response. Please retry.", exact=True).wait_for()
                    page.unroute("**/api/tutoring", broken)
                    for body, expected_error in [("null", "The server returned an invalid response. Please retry."), ("[]", "The server returned an invalid response. Please retry."), ('{"reply":42}', "No response available. Please retry.")]:
                        def make_invalid(response_body):
                            def invalid_response(route):
                                route.fulfill(status=200, body=response_body, content_type="application/json")
                            return invalid_response
                        invalid = make_invalid(body)
                        page.route("**/api/tutoring", invalid)
                        page.locator("#question").fill("Response schema check")
                        page.locator("#send").click()
                        page.wait_for_function("!document.getElementById('send').disabled")
                        assert page.locator("#messages > .msg").last.locator(".message-content").inner_text() == expected_error
                        page.unroute("**/api/tutoring", invalid)
                    def disconnected(route):
                        route.abort()
                    page.route("**/api/tutoring", disconnected)
                    page.locator("#question").fill("Network failure")
                    page.locator("#send").click()
                    page.get_by_text("Cannot reach the server. Check that Flask is running.", exact=True).wait_for()
                    page.unroute("**/api/tutoring", disconnected)
                    assert page.locator("#send").is_enabled()
                    page.locator("#newChat").click()
                    assert page.locator("#suggestions").is_visible()
                    page.set_viewport_size({"width": 390, "height": 844})
                    assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")

                    # Tutoring works even when browser storage is unavailable.
                    page.add_init_script("if(location.pathname==='/agents/tutoring'){Storage.prototype.getItem=()=>{throw new Error('blocked')};Storage.prototype.setItem=()=>{throw new Error('blocked')}}")
                    page.reload()
                    page.locator("#question").fill("Explain neural networks")
                    page.locator("#send").click()
                    page.locator(".msg.bot pre code").wait_for()

                    for name, button, expected in [("academic", "Open academic advisor", "Academic offline reply"), ("career", "Explore career support", "Career offline reply"), ("success", "Explore student resources", "Success offline reply")]:
                        before = len(trace)
                        page.get_by_role("link", name="Student Hub").click()
                        page.get_by_role("button", name=button).click()
                        page.wait_for_url(base + "/agents/" + name)
                        page.locator("#question").fill("Offline agent question")
                        page.locator("#send").click()
                        page.get_by_text(expected, exact=True).wait_for()
                        endpoint = "adviser" if name == "academic" else name
                        assert page.request.post(base + "/api/" + endpoint, data={"question": ""}).status == 400
                        if name in ("career", "success"):
                            state["mode"] = name + "_failure"
                            page.locator("#question").fill("Offline failure recovery")
                            page.locator("#send").click()
                            page.get_by_role("button", name="Retry", exact=True).wait_for()
                            assert "Synthetic provider diagnostic" not in page.locator("#messages").inner_text()
                            state["mode"] = "ok"
                            page.get_by_role("button", name="Retry", exact=True).click()
                            page.wait_for_function("!document.querySelector('.msg.error') && !document.getElementById('send').disabled")
                        assert len(trace) == before
                    page.get_by_role("link", name="Student Hub").click()
                    page.get_by_role("button", name="Explore learning support").click()
                    page.evaluate("() => { window.name = 'offline-pending'; const abort = AbortController.prototype.abort; AbortController.prototype.abort = function(...args) { window.name = 'offline-cancelled'; return abort.apply(this, args); }; }")
                    page.locator("#question").fill("cancel navigation")
                    page.locator("#send").click()
                    page.locator("[aria-busy=true]").wait_for()
                    # Observe abort before document teardown; browser network-event
                    # delivery during pagehide varies and cannot prove server cancellation.
                    page.evaluate("document.querySelector('header a').addEventListener('click', event => event.preventDefault(), {once:true})")
                    page.get_by_role("link", name="Student Hub").click()
                    assert page.evaluate("window.name") == "offline-cancelled"
                    page.get_by_role("link", name="Student Hub").click()
                    page.wait_for_url(base + "/chat")
                    assert page.locator(".service-card").count() == 4
                    browser.close()

                # Separate HTTP requests run concurrently without conversation state.
                def request(q):
                    with app.test_client() as client:
                        return client.post("/api/tutoring", json={"question": q}).json["reply"]
                with ThreadPoolExecutor(max_workers=2) as pool:
                    replies = list(pool.map(request, ["binary search", "SQL queries"]))
                assert "binary search" in replies[0] and "SQL queries" not in replies[0]
                assert "SQL queries" in replies[1] and "binary search" not in replies[1]
                print("PASS: real Flask/Chrome hub-to-Tutoring coordinator-specialist-QA journey; validation, loading, duplicate guard, Markdown/XSS, recovery, storage denial, agent switching, concurrent isolation")
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=5)


if __name__ == "__main__":
    run(legacy_only="--legacy-regression" in sys.argv)
