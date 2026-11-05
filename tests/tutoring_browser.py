"""Manual offline browser test; every URL is intercepted, including CDN and API."""
import json
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
HTML = (ROOT / "frontend/agents/tutoring/index.html").read_text(encoding="utf-8")
ASSETS = ROOT / ".venv-step3/browser-assets"


def run():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(executable_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe", headless=True)
        page = browser.new_page()
        state = {"calls": 0, "fail": False, "assets": True}
        answer = "## Steps\n1. Define a variable.\n\n```python\nx = 1\n```\n<img src=x onerror='window.pwned=1'>\n[bad](javascript:alert(1))"

        def route(request):
            url = request.request.url
            if url == "https://tutoring.test/agents/tutoring":
                request.fulfill(body=HTML, content_type="text/html")
            elif "/npm/marked@" in url or "/npm/dompurify@" in url:
                if not state["assets"]:
                    request.abort()
                else:
                    filename = "marked.js" if "/marked@" in url else "purify.js"
                    request.fulfill(body=(ASSETS / filename).read_text(encoding="utf-8"), content_type="application/javascript")
            elif url == "https://tutoring.test/api/tutoring":
                state["calls"] += 1
                assert isinstance(request.request.post_data_json["question"], str)
                request.fulfill(status=503 if state["fail"] else 200, content_type="application/json",
                                body=json.dumps({"error": "Temporary test error"} if state["fail"] else {"reply": answer, "implemented": True}))
            else:
                request.abort()

        page.route("**/*", route)
        page.goto("https://tutoring.test/agents/tutoring")
        page.locator("#send").click()
        assert state["calls"] == 0
        page.locator("#question").fill("Python loops")
        page.evaluate("document.getElementById('form').requestSubmit(); document.getElementById('question').value='duplicate'; document.getElementById('form').requestSubmit();")
        page.locator(".msg.bot pre code").wait_for()
        assert state["calls"] == 1
        assert page.locator(".msg.bot h2").inner_text() == "Steps"
        assert page.locator(".msg.bot pre code").inner_text().strip() == "x = 1"
        assert page.locator(".msg.bot [onerror], .msg.bot a[href^='javascript:']").count() == 0
        assert page.evaluate("window.pwned || 0") == 0
        assert page.get_by_role("button", name="Copy", exact=True).count() == 1
        state["fail"] = True
        page.locator("#question").fill("SQL")
        page.locator("#send").click()
        page.get_by_role("button", name="Retry", exact=True).wait_for()
        assert page.locator(".msg.error").inner_text().startswith("Temporary test error")
        assert page.locator("#send").is_enabled()
        state["fail"] = False
        page.get_by_role("button", name="Retry", exact=True).click()
        page.wait_for_function("!document.querySelector('.msg.error') && !document.getElementById('send').disabled")
        assert state["calls"] == 3
        page.locator("#newChat").click()
        assert page.locator("#suggestions").is_visible()
        page.evaluate("() => { const realTimeout = window.setTimeout; window.setTimeout = (fn, ms, ...args) => realTimeout(fn, ms === 150000 ? 50 : ms, ...args); }")
        page.evaluate("() => { window.realFetch = window.fetch; window.fetch = (_, options) => new Promise((resolve, reject) => options.signal.addEventListener('abort', () => reject(new DOMException('Aborted', 'AbortError')))); }")
        page.locator("#question").fill("Timeout example")
        page.locator("#send").click()
        page.get_by_text("Tutoring timed out. Please try again.", exact=True).wait_for()
        assert page.locator("#send").is_enabled()
        page.evaluate("() => { window.fetch = window.realFetch; }")
        page.set_viewport_size({"width": 390, "height": 844})
        assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth")
        state["assets"] = False
        page.reload()
        page.locator("#question").fill("Python")
        page.locator("#send").click()
        page.locator(".msg.bot").wait_for()
        assert page.locator(".msg.bot pre").count() == 0
        assert "```python" in page.locator(".msg.bot .message-content").inner_text()
        assert page.locator(".msg.bot .message-content").evaluate("node => getComputedStyle(node).whiteSpace") == "pre-wrap"
        browser.close()
        print("PASS: offline Chrome send/empty/duplicate guard, Markdown/code, XSS sanitization, API error/retry/recovery, abort timeout recovery, copy control, new chat, mobile overflow, missing-CDN fallback")


if __name__ == "__main__":
    run()
