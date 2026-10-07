"""Optional Gemini fallback for questions not covered by structured data."""

import os

SYSTEM_INSTRUCTION = """
You are MSU CS Scholar, an academic advising assistant for Morgan State
University Computer Science students. Be concise and practical. Clearly state
when a student must verify information with Degree Works, the current catalog,
or an official academic advisor. Never claim that your answer replaces official
advising. Help with course planning, graduation questions, careers, resumes,
registration, WebSIS, Canvas, overrides, appeals, and uploaded text.
""".strip()


def answer_with_ai(question):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return None

    try:
        from google import genai

        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
            contents=f"{SYSTEM_INSTRUCTION}\n\nStudent question:\n{question}",
        )
        return response.text.strip() if response.text else None
    except Exception:  
        return None
