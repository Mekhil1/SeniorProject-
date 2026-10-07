"""Read-only advising queries against the curriculum database."""

import re
import sqlite3
from contextlib import closing

from flask import current_app

SEMESTER_WORDS = {
    "first": 1, "1st": 1, "second": 2, "2nd": 2,
    "third": 3, "3rd": 3, "fourth": 4, "4th": 4,
    "fifth": 5, "5th": 5, "sixth": 6, "6th": 6,
    "seventh": 7, "7th": 7, "eighth": 8, "8th": 8,
}


def connect():
    connection = sqlite3.connect(current_app.config["DATABASE"])
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def detect_semester(question):
    normalized = question.lower()
    numeric = re.search(r"semester\s*([1-8])", normalized)
    if numeric:
        return int(numeric.group(1))
    for word, number in SEMESTER_WORDS.items():
        if re.search(rf"\b{re.escape(word)}\s+semester\b", normalized):
            return number
    if any(term in normalized for term in ("freshman", "first year", "1st year")):
        return 1
    return None


def answer_from_database(question):
    q = question.lower().strip()
    semester = detect_semester(q)

    with closing(connect()) as connection:
        if semester or any(
            phrase in q for phrase in ("what classes", "courses should i take", "course plan")
        ):
            return _semester_plan(connection, semester or 1)

        if any(term in q for term in ("graduation", "graduate", "degree requirements")):
            rows = connection.execute(
                "SELECT requirement_name, description FROM graduation_requirements "
                "ORDER BY requirement_id"
            ).fetchall()
            return _format_rows(
                "Graduation requirements:",
                rows,
                lambda row: f"{row['requirement_name']}: {row['description']}",
            )

        if "math" in q:
            rows = connection.execute(
                "SELECT course_code, course_title, credits FROM courses "
                "WHERE course_code LIKE 'MATH%' ORDER BY course_code"
            ).fetchall()
            return _format_courses("Required math courses:", rows)

        if "elective" in q:
            rows = connection.execute(
                "SELECT course_code, course_title, credits, elective_group FROM courses "
                "WHERE category = 'Elective' ORDER BY elective_group, course_code"
            ).fetchall()
            return _format_rows(
                "Computer Science electives:",
                rows,
                lambda row: (
                    f"Group {row['elective_group']}: {row['course_code']} "
                    f"{row['course_title']} ({row['credits']} credits)"
                ),
            )

        career_answer = _career_recommendations(connection, q)
        if career_answer:
            return career_answer

        if any(term in q for term in ("career", "job")):
            rows = connection.execute(
                "SELECT job_title, description FROM career_paths ORDER BY job_title"
            ).fetchall()
            return _format_rows(
                "Computer Science career paths:",
                rows,
                lambda row: f"{row['job_title']}: {row['description']}",
            )

    return None


def _semester_plan(connection, semester):
    rows = connection.execute(
        """
        SELECT s.year_label, s.term_label, c.course_code, c.course_title,
               c.credits, cc.placeholder_label, cc.requirement_type
        FROM curriculum_courses AS cc
        JOIN semesters AS s ON cc.semester_id = s.semester_id
        LEFT JOIN courses AS c ON cc.course_id = c.course_id
        WHERE s.semester_number = ?
        ORDER BY cc.curriculum_id
        """,
        (semester,),
    ).fetchall()
    if not rows:
        return None
    lines = [f"{rows[0]['year_label']} {rows[0]['term_label']} recommended courses:"]
    for row in rows:
        if row["course_code"]:
            lines.append(
                f"- {row['course_code']}: {row['course_title']} ({row['credits']} credits)"
            )
        else:
            lines.append(f"- {row['placeholder_label']} ({row['requirement_type']})")
    return "\n".join(lines)


def _career_recommendations(connection, question):
    keywords = connection.execute(
        "SELECT DISTINCT career_keyword FROM career_course_recommendations"
    ).fetchall()
    match = next((row[0] for row in keywords if row[0] in question), None)
    if not match:
        return None
    rows = connection.execute(
        """
        SELECT career_title, course_code, reason
        FROM career_course_recommendations
        WHERE career_keyword = ?
        ORDER BY recommendation_id
        """,
        (match,),
    ).fetchall()
    return _format_rows(
        f"Recommended courses for {rows[0]['career_title']}:",
        rows,
        lambda row: f"{row['course_code']}: {row['reason']}",
    )


def _format_courses(title, rows):
    return _format_rows(
        title,
        rows,
        lambda row: f"{row['course_code']}: {row['course_title']} ({row['credits']} credits)",
    )


def _format_rows(title, rows, formatter):
    if not rows:
        return None
    return "\n".join([title, *(f"- {formatter(row)}" for row in rows)])
