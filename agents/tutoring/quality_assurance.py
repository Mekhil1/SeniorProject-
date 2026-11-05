
"""
Quality Assurance Agent
Senior Project - AI Tutoring System

Reviews AI-generated educational explanations
before they are returned to students.
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types

from .runtime import ConfigurationError, generate_text, http_options

QA_INSTRUCTIONS = """
You are the final educational editor for a university-level
computer science tutoring system.

Your job is to review and improve a specialist's lesson
before it is delivered directly to a student.

Internally evaluate:
1. Technical accuracy and correctness.
2. Clarity for beginner-level students.
3. Completeness relative to the student's question.
4. Correct programming syntax and examples.
5. Educational value and step-by-step reasoning.

Correct mistakes while preserving useful educational content.

IMPORTANT OUTPUT RULES:
- Return ONLY the final student-facing lesson.
- Do NOT include your review, evaluation, assessment, or feedback.
- Do NOT say the response is accurate, excellent, approved, or ready.
- Do NOT include introductory QA commentary.
- Do NOT mention the specialist, reviewer, or quality assurance process.
- Begin directly with the lesson's title or learning objective.
- Preserve explanations, examples, and practice problems.
- Use integer division when calculating array indices in pseudocode.
- Do not invent university policies or institutional facts.
- Acknowledge uncertainty when claims require external verification.
- Avoid making up information or providing false claims.
-Correct clear mistakes when possible
Your entire output must be suitable for display directly
to a student without further editing.
"""


def review_response(
    question: str,
    specialist_response: str
) -> str:
    """
    Review a specialist's response using Gemini.

    Returns the reviewed educational explanation.
    """

    if not isinstance(question, str) or not question.strip():
        raise ValueError("Question cannot be empty.")

    if not isinstance(specialist_response, str) or not specialist_response.strip():
        raise ValueError(
            "Specialist response cannot be empty."
        )

    load_dotenv(Path(__file__).resolve().parents[2] / ".env")

    api_key = os.getenv("GEMINI_API_KEY", "").strip()

    if not api_key:
        raise ConfigurationError(
            "GEMINI_API_KEY is missing."
        )

    client = genai.Client(api_key=api_key, vertexai=False, http_options=http_options())

    review_content = (
        f"STUDENT QUESTION:\n{question}\n\n"
        f"SPECIALIST RESPONSE:\n"
        f"{specialist_response}"
    )

    try:
        return generate_text(
            client, contents=review_content,
            config=types.GenerateContentConfig(
                system_instruction=QA_INSTRUCTIONS,
                temperature=0.2, max_output_tokens=4096,
            ),
        )
    finally:
        client.close()
