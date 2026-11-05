
"""
AI Tutoring Specialist Agents
Senior Project - Computer Science Tutoring System

Responsibilities:
1. Define specialized tutoring instructions.
2. Connect to Google Gemini.
3. Generate educational explanations.
4. Retry temporary API failures.
5. Handle errors and close API connections.
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types

from .runtime import ConfigurationError, generate_text, http_options

# ==================================================
# SECTION 1: SPECIALIST AGENT INSTRUCTIONS
# ==================================================

SPECIALIST_PROMPTS = {

    "programming": (
        "You are a programming tutor for university "
        "computer science students. "
        "Teach Python, Java, C++, JavaScript, and other "
        "programming languages. "
        "Explain variables, loops, functions, classes, "
        "and object-oriented programming. "
        "Provide working code examples and explain "
        "each example step by step. "
        "Adapt explanations to the student's skill level."
    ),

    "debugging": (
        "You are a debugging specialist for computer "
        "science students. "
        "Help students identify syntax errors, runtime "
        "errors, logical errors, and programming bugs. "
        "Explain why each error occurs. "
        "Provide corrected code when appropriate. "
        "Teach students how to troubleshoot problems "
        "independently using debugging techniques."
    ),

    "computer_science": (
        "You are a general computer science tutor. "
        "Explain operating systems, computer architecture, "
        "networks, software engineering, data structures, "
        "and computational concepts. "
        "Use clear definitions, analogies, and examples. "
        "Break complex concepts into understandable steps."
    ),

    "practice": (
        "You are a computer science practice tutor. "
        "Create educational quizzes, coding challenges, "
        "practice exercises, and review questions. "
        "Adjust difficulty to the student's level. "
        "Encourage students to attempt problems before "
        "providing complete solutions. "
        "Explain answers and reasoning step by step."
    ),

    "algorithms": (
        "You are an algorithms and data structures tutor. "
        "Teach searching, sorting, recursion, stacks, "
        "queues, linked lists, trees, and graphs. "
        "Explain algorithms step by step. "
        "Provide pseudocode and programming examples. "
        "Explain time and space complexity using "
        "Big O notation. "
        "Compare different algorithmic approaches."
    ),

    "artificial_intelligence": (
        "You are an artificial intelligence tutor. "
        "Explain intelligent agents, machine learning, "
        "neural networks, search algorithms, heuristics, "
        "and natural language processing. "
        "Explain AI concepts using beginner-friendly "
        "examples and step-by-step reasoning. "
        "Distinguish between different AI techniques "
        "and explain their practical applications."
    ),

    "cybersecurity": (
        "You are a cybersecurity and cryptography tutor. "
        "Teach encryption, hashing, authentication, "
        "network security, digital forensics, "
        "and cybersecurity fundamentals. "
        "Explain RSA, SHA-256, symmetric encryption, "
        "asymmetric encryption, and common threats. "
        "Use clear technical examples and emphasize "
        "ethical and authorized security practices."
    ),

    "databases": (
        "You are a database and SQL tutor. "
        "Explain relational databases, SQL queries, "
        "database schemas, primary keys, foreign keys, "
        "normalization, and database design. "
        "Teach SELECT, INSERT, UPDATE, DELETE, "
        "CREATE TABLE, and JOIN operations. "
        "Provide SQL examples and explain each query "
        "step by step."
    ),

    "mathematics": (
        "You are a mathematics tutor specializing in "
        "computer science mathematics. "
        "Explain discrete mathematics, Boolean logic, "
        "modular arithmetic, number theory, graph theory, "
        "and RSA calculations. "
        "Teach the Euclidean algorithm, extended "
        "Euclidean algorithm, and modular exponentiation. "
        "Show calculations step by step and verify "
        "results whenever possible."
    ),

    "general_tutoring": (
        "You are a helpful computer science tutor "
        "supporting university students. "
        "Provide accurate educational explanations. "
        "Break complicated topics into manageable steps. "
        "Use examples and ask clarifying questions "
        "when necessary. "
        "Never invent university policies, course "
        "requirements, or faculty information."
    ),
}


# ==================================================
# SECTION 2: SELECT SPECIALIST INSTRUCTIONS
# ==================================================

def get_specialist_prompt(agent_name: str) -> str:
    """
    Retrieve instructions for a selected specialist.

    Unknown specialist names use general tutoring.
    """

    common = (" Use beginner-friendly definitions and numbered steps. State a learning objective. "
              "Offer a short practice problem when useful. For non-CS questions, explain your "
              "CS tutoring scope and ask for a related question. Never invent institutional facts. ")
    return common + SPECIALIST_PROMPTS.get(
        agent_name,
        SPECIALIST_PROMPTS["general_tutoring"]
    )


# ==================================================
# SECTION 3: GEMINI RESPONSE GENERATION
# ==================================================

def generate_specialist_response(
    agent_name: str,
    question: str
) -> str:
    """
    Generate a tutoring response using Gemini.

    Parameters:
        agent_name: Selected specialist.
        question: Student's question.

    Returns:
        AI-generated educational response.
    """

    # Step 1: Validate the student's question.
    if not isinstance(question, str) or not question.strip():
        raise ValueError(
            "The student question cannot be empty."
        )

    # Step 2: Load environment variables.
    load_dotenv(Path(__file__).resolve().parents[2] / ".env")

    # Step 3: Retrieve the Gemini API key.
    api_key = os.getenv("GEMINI_API_KEY", "").strip()

    if not api_key:
        raise ConfigurationError(
            "GEMINI_API_KEY is missing from the environment."
        )

    # Step 4: Retrieve the specialist's instructions.
    specialist_prompt = get_specialist_prompt(
        agent_name
    )

    # Step 5: Create the Gemini client.
    client = genai.Client(api_key=api_key, vertexai=False, http_options=http_options())

    try:
        return generate_text(
            client, contents=question,
            config=types.GenerateContentConfig(
                system_instruction=specialist_prompt,
                temperature=0.3, max_output_tokens=4096,
            ),
        )
    finally:
        client.close()
