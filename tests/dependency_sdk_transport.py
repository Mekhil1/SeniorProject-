"""Exercise real Gen AI request serialization with an in-memory HTTP transport."""
import socket

import httpx
from google import genai
from google.auth.credentials import AnonymousCredentials
from google.genai import types


def blocked(*args, **kwargs):
    raise AssertionError("Real socket access forbidden")


def run():
    socket.socket.connect = blocked
    socket.create_connection = blocked
    calls = []

    def respond(request):
        import json
        payload = json.loads(request.content)
        assert payload["contents"][0]["parts"][0]["text"] == "Explain Python variables"
        calls.append(payload)
        return httpx.Response(200, json={
            "candidates": [{"content": {"role": "model", "parts": [{"text": "A variable names a value."}]}, "finishReason": "STOP"}]
        })

    transport = httpx.Client(transport=httpx.MockTransport(respond))
    client = genai.Client(api_key="offline-placeholder", vertexai=False,
                         http_options=types.HttpOptions(httpx_client=transport, timeout=20000,
                                                       retry_options=types.HttpRetryOptions(attempts=1)))
    try:
        response = client.models.generate_content(
            model="gemini-3.5-flash-lite", contents="Explain Python variables",
            config=types.GenerateContentConfig(system_instruction="Beginner tutor", max_output_tokens=4096),
        )
        assert response.text == "A variable names a value."
        assert len(calls) == 1
        print("PASS: real SDK GenerateContent serialization and response parsing through in-memory HTTP mock")
    finally:
        client.close()
        transport.close()
    vertex = genai.Client(vertexai=True, project="offline-project", location="global", credentials=AnonymousCredentials())
    try:
        assert callable(vertex.models.generate_content)
        print("PASS: Vertex/global client construction with anonymous offline credentials (no request)")
    finally:
        vertex.close()


if __name__ == "__main__":
    run()
