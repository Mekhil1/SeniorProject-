"""Local, conservative Degree Works PDF parser. No AI or external requests."""
from __future__ import annotations
import io
import re
from datetime import datetime
import pdfplumber

COURSE = re.compile(r"\b([A-Z]{2,5})\s+(\d{3}[A-Z]?)\b")
TERM = r"(?:FALL|SPRING|SUMMER|WINTER)\s+20\d{2}"
# A course entry with a grade, credits and term on the same line.
RECORD = re.compile(
    r"\b(?P<dept>[A-Z]{2,5})\s+(?P<num>\d{3}[A-Z]?)\b"
    r"(?P<title>.*?)\s+"
    r"(?P<grade>IP|[ABCDFW][+-]?)\s+"
    r"(?P<credits>\(?\d+(?:\.\d+)?\)?)\s+"
    r"(?P<term>" + TERM + r")\b", re.I
)

def _one(pattern, text, default=None):
    match = re.search(pattern, text, re.I | re.M)
    return match.group(1).strip() if match else default

def parse_degreeworks(pdf_bytes: bytes) -> dict:
    if not pdf_bytes.startswith(b"%PDF-"):
        raise ValueError("Upload a valid PDF document.")
    if len(pdf_bytes) > 5 * 1024 * 1024:
        raise ValueError("PDF exceeds the 5 MB limit.")
    try:
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            if len(pdf.pages) > 15:
                raise ValueError("PDF exceeds the 15-page limit.")
            text = "\n".join(page.extract_text(x_tolerance=2, y_tolerance=3) or "" for page in pdf.pages)
    except ValueError:
        raise
    except Exception as exc:
        raise ValueError("Unable to read this PDF. Please export a text-based Degree Works PDF.") from exc
    if "Degree progress" not in text or "Major in Computer Science" not in text:
        raise ValueError("This does not appear to be a supported Computer Science Degree Works report.")

    # Restrict records to the main audit and stop before duplicate 'Insufficient' and 'In-progress' summaries.
    main = re.split(r"\nInsufficient\s*\n|\nIn-progress\s*\n", text, maxsplit=1, flags=re.I)[0]
    courses = {}
    for line in main.splitlines():
        m = RECORD.search(line)
        if not m:
            continue
        code = f"{m['dept'].upper()} {m['num'].upper()}"
        grade = m['grade'].upper()
        status = "in_progress" if grade == "IP" else "withdrawn" if grade == "W" else "completed" if grade in {"A", "A-", "B+", "B", "B-", "C+", "C", "C-"} else "graded_not_verified" if grade in {"D+", "D", "D-", "F"} else "unknown"
        item = {"code": code, "title": m['title'].strip(), "grade": grade,
                "credits": float(m['credits'].strip('()')), "term": m['term'].upper(), "status": status}
        # Duplicates appear in several audit sections; retain in-progress over past completed only if appropriate.
        if code not in courses or courses[code]['status'] != 'in_progress':
            courses[code] = item

    # 'Insufficient' explicitly lists withdrawn and non-applicable attempts.
    insufficient = re.search(r"\nInsufficient\b(.*?)(?:\nIn-progress\b|\nExceptions\b|\Z)", text, re.S | re.I)
    if insufficient:
        for line in insufficient.group(1).splitlines():
            m = RECORD.search(line)
            if m and m['grade'].upper() == 'W':
                code = f"{m['dept'].upper()} {m['num'].upper()}"
                if code not in courses:
                    courses[code] = {"code": code, "title": m['title'].strip(), "grade": "W", "credits": 0, "term": m['term'].upper(), "status": "withdrawn"}

    # Explicit unmet requirements only; do not mistake a list of options for completed courses.
    missing = []
    for line in text.splitlines():
        if 'Still needed:' not in line:
            continue
        requirement = line.split('Still needed:', 1)[1].strip()
        if requirement.lower().startswith('see major'):
            continue
        if requirement and requirement not in missing:
            missing.append(requirement)
    # PDF wraps the Group B alternatives to the next line; preserve the option list.
    if re.search(r"Still needed:\s*1 Class in COSC 323", text, re.I):
        missing = [x for x in missing if not x.startswith('1 Class in COSC 323')]
        missing.append('Group B elective: one approved course from COSC 323, 332, 338, 383, 385, 386, MATH 313, or EEGR 317 (verify audit exceptions and applicability).')
    if re.search(r"Still needed:\s*1 Class in COSC 352", text, re.I):
        missing = [x for x in missing if not x.startswith('1 Class in COSC 352')]
        missing.insert(0, 'COSC 352 — Organization of Programming Languages')

    progress = re.search(r"Degree progress.*?(\d{1,3})%\s+(\d{1,3})%.*?Requirements\s+Credits", text, re.I | re.S)
    degree = re.search(r"Bachelor of Science\s*(COMPLETE|INCOMPLETE).*?Credits required:\s*(\d+)\s+Credits applied:\s*(\d+).*?Catalog year:\s*([^\n]+?)\s+GPA:\s*([\d.]+)", text, re.I | re.S)
    audit = _one(r"Audit date\s+([^\n]+)", text)
    result = {
        "source": "Degree Works PDF (local parsing)",
        "audit_date": audit,
        "catalog_year": degree.group(4).strip() if degree else None,
        "degree_status": degree.group(1).upper() if degree else "UNVERIFIED",
        "requirements_percent": int(progress.group(1)) if progress else None,
        "credits_percent": int(progress.group(2)) if progress else None,
        "credits_required": int(degree.group(2)) if degree else None,
        "credits_applied": int(degree.group(3)) if degree else None,
        "gpa": float(degree.group(5)) if degree else None,
        "courses": sorted(courses.values(), key=lambda c: (c['status'], c['code'])),
        "missing_requirements": missing,
        "warnings": ["Unofficial audit; verify graduation eligibility with the registrar and academic advisor.",
                     "In-progress courses are not completed courses.",
                     "Course-level parsing is best-effort; verify every status against the original PDF."],
    }
    if not progress or not degree:
        result['warnings'].append('Some summary fields could not be verified; they are left blank.')
    return result
