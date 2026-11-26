
"""
AI Tutoring Coordinator

Selects the appropriate specialist based on
the student's computer science question.
"""

import re
from dataclasses import dataclass


@dataclass
class AgentSelection:
    agent_name: str
    topic: str


AGENT_KEYWORDS = {
    "debugging": [
        "debug", "debugging", "bug", "error",
        "exception", "traceback", "fix my code",
        "not working"
    ],

    "practice": [
        "practice", "quiz", "exercise",
        "test me", "practice problem",
        "practice questions"
    ],

    "programming": [
        "python", "java", "javascript",
        "c++", "variable", "loop",
        "function", "coding", "programming"
    ],

    "algorithms": [
        "algorithm", "binary search", "sorting",
        "stack", "queue", "linked list",
        "data structure", "recursion",
        "big o", "time complexity"
    ],

    "cybersecurity": [
        "security", "cybersecurity", "network",
        "encryption", "firewall", "phishing",
        "cryptography", "hash function"
    ],

    "databases": [
        "database", "sql", "mysql", "table",
        "primary key", "foreign key", "query"
    ],

    "mathematics": [
        "discrete math", "logic", "modular",
        "rsa", "set theory", "graph theory"
    ],

    "artificial_intelligence": [
        "machine learning", "artificial intelligence",
        "neural network", "classification",
        "ai agent", "a star search"
    ],

    "computer_science": [
        "computer science", "operating system",
        "computer architecture", "data structures"
    ]
}


def select_agent(question: str) -> AgentSelection:
    """
    Choose a specialist using keyword matching.
    """

    question_lower = question.lower()

    # Keep task intent first, then prefer a subject over language-only hints.
    priority = ["debugging", "practice", "artificial_intelligence", "databases",
                "mathematics", "algorithms", "cybersecurity",
                "computer_science", "programming"]
    aliases = {
        "algorithms": ["trees", "graphs", "arrays", "data structures", "algorithms", "binary trees"],
        "artificial_intelligence": ["neural networks", "ml", "deep learning"],
        "computer_science": ["networks", "network", "computer systems", "memory", "cpu", "operating systems"],
        "mathematics": ["proof", "proofs", "sets", "discrete mathematics"],
    }
    for agent_name in priority:
        keywords = list(AGENT_KEYWORDS[agent_name]) + aliases.get(agent_name, [])
        if agent_name == "cybersecurity":
            keywords.remove("network")  # General networking is not necessarily security.
        for keyword in keywords:
            if re.search(r"(?<!\w)" + re.escape(keyword) + r"(?!\w)", question_lower):
                return AgentSelection(agent_name=agent_name, topic=question)

    return AgentSelection(
        agent_name="general_tutoring",
        topic=question
    )


if __name__ == "__main__":

    questions = [
        "How do I write a Python function?",
        "Help me debug an error in my code",
        "Explain data structures",
        "Give me a practice problem"
    ]

    for question in questions:
        selection = select_agent(question)

        print("Question:", question)
        print("Selected agent:", selection.agent_name)
        print()
