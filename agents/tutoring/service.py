"""Coordinate the AI tutoring workflow."""

from .coordinator import select_agent
from .quality_assurance import review_response
from .specialists import generate_specialist_response


def answer(question: str) -> str:
    """Generate and review a tutoring response."""

    if not isinstance(question, str) or not question.strip():
        raise ValueError("Question cannot be empty.")

    question = question.strip()

    # Step 1: Select the appropriate specialist.
    selection = select_agent(question)

    # Step 2: Generate the specialist's explanation.
    specialist_response = generate_specialist_response(
        selection.agent_name,
        question,
    )

    # Step 3: Review the explanation for clarity and accuracy.
    reviewed_response = review_response(
        question,
        specialist_response,
    )

    # Step 4: Return the final explanation.
    return reviewed_response
