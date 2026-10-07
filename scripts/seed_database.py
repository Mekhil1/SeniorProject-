import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[1] / "student_advisor.db"
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.executescript("""
PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS career_course_recommendations;
DROP TABLE IF EXISTS career_paths;
DROP TABLE IF EXISTS graduation_requirements;
DROP TABLE IF EXISTS student_selected_courses;
DROP TABLE IF EXISTS student_progress;
DROP TABLE IF EXISTS students;
DROP TABLE IF EXISTS curriculum_courses;
DROP TABLE IF EXISTS courses;
DROP TABLE IF EXISTS semesters;
DROP TABLE IF EXISTS elective_groups;

CREATE TABLE semesters (
    semester_id INTEGER PRIMARY KEY,
    year_label TEXT NOT NULL,
    term_label TEXT NOT NULL,
    semester_number INTEGER NOT NULL UNIQUE
);

CREATE TABLE elective_groups (
    group_code TEXT PRIMARY KEY,
    group_name TEXT NOT NULL,
    min_required INTEGER NOT NULL
);

CREATE TABLE courses (
    course_id INTEGER PRIMARY KEY AUTOINCREMENT,
    course_code TEXT UNIQUE,
    course_title TEXT NOT NULL,
    credits INTEGER NOT NULL,
    category TEXT NOT NULL,
    elective_group TEXT,
    FOREIGN KEY (elective_group) REFERENCES elective_groups(group_code)
);

CREATE TABLE curriculum_courses (
    curriculum_id INTEGER PRIMARY KEY AUTOINCREMENT,
    semester_id INTEGER NOT NULL,
    course_id INTEGER,
    placeholder_label TEXT,
    requirement_type TEXT NOT NULL,
    is_choice INTEGER NOT NULL DEFAULT 0,
    choice_group TEXT,
    FOREIGN KEY (semester_id) REFERENCES semesters(semester_id),
    FOREIGN KEY (course_id) REFERENCES courses(course_id),
    FOREIGN KEY (choice_group) REFERENCES elective_groups(group_code)
);

CREATE TABLE students (
    student_id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    entry_term TEXT,
    major TEXT DEFAULT 'Computer Science',
    gpa REAL DEFAULT 0.0
);

CREATE TABLE student_selected_courses (
    selection_id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    semester_id INTEGER NOT NULL,
    course_id INTEGER NOT NULL,
    status TEXT NOT NULL DEFAULT 'planned',
    UNIQUE(student_id, semester_id, course_id),
    FOREIGN KEY (student_id) REFERENCES students(student_id),
    FOREIGN KEY (semester_id) REFERENCES semesters(semester_id),
    FOREIGN KEY (course_id) REFERENCES courses(course_id)
);

CREATE TABLE student_progress (
    progress_id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    completed_course_code TEXT NOT NULL,
    completed_course_title TEXT NOT NULL,
    credits INTEGER NOT NULL,
    term_completed TEXT NOT NULL,
    FOREIGN KEY (student_id) REFERENCES students(student_id)
);

CREATE TABLE graduation_requirements (
    requirement_id INTEGER PRIMARY KEY AUTOINCREMENT,
    requirement_name TEXT NOT NULL,
    required_credits INTEGER,
    required_gpa REAL,
    description TEXT NOT NULL
);

CREATE TABLE career_paths (
    career_id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_title TEXT NOT NULL,
    description TEXT NOT NULL
);

CREATE TABLE career_course_recommendations (
    recommendation_id INTEGER PRIMARY KEY AUTOINCREMENT,
    career_keyword TEXT NOT NULL,
    career_title TEXT NOT NULL,
    course_code TEXT NOT NULL,
    reason TEXT NOT NULL
);
""")

semesters = [
    (1, "Freshman", "First Semester", 1),
    (2, "Freshman", "Second Semester", 2),
    (3, "Sophomore", "Third Semester", 3),
    (4, "Sophomore", "Fourth Semester", 4),
    (5, "Junior", "Fifth Semester", 5),
    (6, "Junior", "Sixth Semester", 6),
    (7, "Senior", "Seventh Semester", 7),
    (8, "Senior", "Eighth Semester", 8),
]

cursor.executemany(
    "INSERT INTO semesters (semester_id, year_label, term_label, semester_number) VALUES (?, ?, ?, ?)",
    semesters
)

elective_groups = [
    ("A", "COSC Group A Electives", 3),
    ("B", "COSC Group B Electives", 2),
    ("C", "COSC Group C Electives", 4),
    ("D", "COSC Group D Electives", 1),
]

cursor.executemany(
    "INSERT INTO elective_groups (group_code, group_name, min_required) VALUES (?, ?, ?)",
    elective_groups
)

courses = [
    ("COSC 111", "Introduction to Computer Science I", 4, "Major", None),
    ("COSC 112", "Introduction to Computer Science II", 4, "Major", None),
    ("COSC 220", "Data Structures and Algorithms", 4, "Major", None),
    ("COSC 241", "Computer Systems and Digital Logic", 3, "Major", None),
    ("COSC 281", "Discrete Structure", 3, "Major", None),
    ("COSC 349", "Computer Networks", 3, "Major", None),
    ("COSC 351", "Cybersecurity", 3, "Major", None),
    ("COSC 352", "Organization of Programming Languages", 3, "Major", None),
    ("COSC 354", "Operating Systems", 3, "Major", None),
    ("COSC 458", "Software Engineering", 3, "Major", None),
    ("COSC 459", "Database Design", 3, "Major", None),
    ("COSC 490", "Senior Project", 3, "Major", None),

    ("ENGL 101", "Composition I", 3, "General Education", None),
    ("ENGL 102", "Composition II", 3, "General Education", None),
    ("MATH 241", "Calculus I", 4, "Supporting Course", None),
    ("MATH 242", "Calculus II", 4, "Supporting Course", None),
    ("MATH 312", "Linear Algebra I", 3, "Supporting Course", None),
    ("MATH 331", "Applied Probability and Statistics", 3, "Supporting Course", None),
    ("COSC 201", "Computer Ethics", 1, "Supporting Course", None),
    ("ORNS 106", "Freshman Orientation for SCMNS Majors", 1, "University Requirement", None),

    ("COSC 238", "Object Oriented Programming", 4, "Elective", "A"),
    ("COSC 239", "Java Programming", 3, "Elective", "A"),
    ("COSC 243", "Computer Architecture", 3, "Elective", "A"),
    ("COSC 251", "Introduction to Data Science", 3, "Elective", "A"),
    ("CLCO 261", "Introduction to Cloud Computing", 3, "Elective", "A"),

    ("COSC 320", "Algorithm Design and Analysis", 3, "Elective", "B"),
    ("COSC 323", "Introduction to Cryptography", 3, "Elective", "B"),
    ("COSC 332", "Introduction to Game Design and Development", 3, "Elective", "B"),
    ("COSC 338", "Mobile App Design & Development", 3, "Elective", "B"),
    ("COSC 383", "Numerical Methods and Programming", 3, "Elective", "B"),
    ("COSC 385", "Theory of Languages and Automata", 3, "Elective", "B"),
    ("COSC 386", "Introduction to Quantum Computing", 3, "Elective", "B"),
    ("MATH 313", "Linear Algebra II", 3, "Elective", "B"),
    ("EEGR 317", "Electronic Circuits", 4, "Elective", "B"),

    ("COSC 470", "Artificial Intelligence", 3, "Elective", "C"),
    ("COSC 472", "Introduction to Machine Learning", 3, "Elective", "C"),
    ("COSC 460", "Computer Graphics", 3, "Elective", "C"),
    ("COSC 480", "Introduction to Image Processing and Analysis", 3, "Elective", "C"),
    ("COSC 486", "Applied Quantum Computing", 3, "Elective", "C"),
    ("COSC 491", "Conference Course", 3, "Elective", "C"),
    ("COSC 498", "Senior Internship", 3, "Elective", "C"),
    ("COSC 499", "Senior Research or Teaching/Tutorial Assistantship", 3, "Elective", "C"),
    ("CLCO 471", "Data Analytics in Cloud", 3, "Elective", "C"),

    ("INSS 391", "IT Infrastructure and Security", 3, "Elective", "D"),
    ("INSS 494", "Information Security and Risk Management", 3, "Elective", "D"),
    ("EEGR 481", "Introduction to Network Security", 3, "Elective", "D"),
    ("EEGR 483", "Introduction to Security Management", 3, "Elective", "D"),
]

cursor.executemany(
    "INSERT INTO courses (course_code, course_title, credits, category, elective_group) VALUES (?, ?, ?, ?, ?)",
    courses
)


def cid(code):
    row = cursor.execute(
        "SELECT course_id FROM courses WHERE course_code = ?",
        (code,)
    ).fetchone()
    return row[0]


curriculum_rows = [
    (1, cid("COSC 111"), None, "Required", 0, None),
    (1, cid("ENGL 101"), None, "Required", 0, None),
    (1, cid("MATH 241"), None, "Required", 0, None),
    (1, None, "CT General Education Requirement", "General Education", 0, None),
    (1, cid("ORNS 106"), None, "Required", 0, None),

    (2, cid("ENGL 102"), None, "Required", 0, None),
    (2, None, "HH General Education Requirement", "General Education", 0, None),
    (2, None, "Phys. Ed Activity or FIN 101 or MIND 101", "University Requirement", 0, None),
    (2, cid("COSC 112"), None, "Required", 0, None),
    (2, cid("MATH 242"), None, "Required", 0, None),

    (3, cid("COSC 220"), None, "Required", 0, None),
    (3, cid("COSC 241"), None, "Required", 0, None),
    (3, None, "AH General Education Requirement", "General Education", 0, None),
    (3, None, "Choose a Group A elective", "Elective Choice", 1, "A"),
    (3, cid("COSC 201"), None, "Required", 0, None),

    (4, cid("COSC 281"), None, "Required", 0, None),
    (4, None, "Choose a Group A elective", "Elective Choice", 1, "A"),
    (4, None, "Choose a Group A elective", "Elective Choice", 1, "A"),
    (4, cid("MATH 312"), None, "Required", 0, None),
    (4, None, "AH General Education Requirement", "General Education", 0, None),

    (5, cid("COSC 349"), None, "Required", 0, None),
    (5, cid("COSC 351"), None, "Required", 0, None),
    (5, cid("COSC 352"), None, "Required", 0, None),
    (5, None, "Choose a Group B elective", "Elective Choice", 1, "B"),
    (5, None, "BP General Education Requirement with lab", "General Education", 0, None),

    (6, cid("COSC 354"), None, "Required", 0, None),
    (6, cid("MATH 331"), None, "Required", 0, None),
    (6, None, "Choose a Group B elective", "Elective Choice", 1, "B"),
    (6, None, "CI General Education Requirement", "General Education", 0, None),
    (6, None, "BP General Education Requirement without lab", "General Education", 0, None),

    (7, cid("COSC 458"), None, "Required", 0, None),
    (7, cid("COSC 459"), None, "Required", 0, None),
    (7, cid("COSC 490"), None, "Required", 0, None),
    (7, None, "Choose a Group C elective", "Elective Choice", 1, "C"),
    (7, None, "SB General Education Requirement", "General Education", 0, None),

    (8, None, "Choose a Group C elective", "Elective Choice", 1, "C"),
    (8, None, "Choose a Group C elective", "Elective Choice", 1, "C"),
    (8, None, "Choose a Group C elective", "Elective Choice", 1, "C"),
    (8, None, "Choose a Group D elective", "Elective Choice", 1, "D"),
    (8, None, "SB General Education Requirement", "General Education", 0, None),
]

cursor.executemany("""
INSERT INTO curriculum_courses
(semester_id, course_id, placeholder_label, requirement_type, is_choice, choice_group)
VALUES (?, ?, ?, ?, ?, ?)
""", curriculum_rows)

graduation_requirements = [
    (
        "Total Credits",
        120,
        2.0,
        "A minimum of 120 credit hours and a 2.0 or higher GPA are required to graduate with a B.S. in Computer Science."
    ),
    (
        "General Education and University Requirements",
        44,
        None,
        "Students must complete 44 credits of general education and university requirements."
    ),
    (
        "Supporting Courses",
        11,
        None,
        "Students must complete 11 credits of supporting courses."
    ),
    (
        "Required Courses for the Computer Science Major",
        65,
        None,
        "Students must complete 65 credits of required Computer Science major courses."
    ),
    (
        "Math Requirements",
        14,
        None,
        "Required math courses are MATH 241 Calculus I, MATH 242 Calculus II, MATH 312 Linear Algebra I, and MATH 331 Applied Probability and Statistics."
    ),
]

cursor.executemany("""
INSERT INTO graduation_requirements
(requirement_name, required_credits, required_gpa, description)
VALUES (?, ?, ?, ?)
""", graduation_requirements)

career_paths = [
    ("Software Developer/Engineer", "Creates, tests, and maintains software applications and systems."),
    ("Cybersecurity Analyst", "Protects computer networks and systems from cyber threats."),
    ("Data Scientist/Analyst", "Uses machine learning and statistics to interpret data for business decisions."),
    ("Systems Analyst", "Evaluates and improves an organization's IT systems."),
    ("Web Developer/Full-Stack Developer", "Designs and builds websites and web applications."),
    ("Database Administrator", "Manages and secures data storage systems."),
    ("AI/Machine Learning Engineer", "Develops artificial intelligence systems."),
    ("IT Project Manager", "Leads technical projects and coordinates teams."),
    ("UX/UI Designer", "Focuses on user experience and interface design for applications."),
    ("DevOps Engineer", "Bridges the gap between software development and IT operations."),
    ("Forensic Computer Analyst", "Investigates digital evidence and computer-related crimes."),
    ("Network Architect", "Designs and builds computer networks for organizations."),
    ("Quality Assurance Analyst", "Tests software to find bugs and improve product quality."),
    ("Technical Writer", "Creates documentation, manuals, and guides for technical products."),
    ("IT Auditor", "Reviews technology systems for security, compliance, and risk."),
]

cursor.executemany("""
INSERT INTO career_paths (job_title, description)
VALUES (?, ?)
""", career_paths)

career_course_recommendations = [
    ("software", "Software Developer/Engineer", "COSC 112", "Builds programming fundamentals."),
    ("software", "Software Developer/Engineer", "COSC 220", "Builds data structures and algorithm skills."),
    ("software", "Software Developer/Engineer", "COSC 352", "Helps with programming languages and software design."),
    ("software", "Software Developer/Engineer", "COSC 458", "Directly supports software engineering skills."),
    ("software", "Software Developer/Engineer", "COSC 459", "Builds database design skills used in applications."),

    ("cybersecurity", "Cybersecurity Analyst", "COSC 351", "Directly supports cybersecurity fundamentals."),
    ("cybersecurity", "Cybersecurity Analyst", "COSC 349", "Builds computer networking knowledge."),
    ("cybersecurity", "Cybersecurity Analyst", "COSC 323", "Supports cryptography and security concepts."),
    ("cybersecurity", "Cybersecurity Analyst", "INSS 391", "Supports IT infrastructure and security."),
    ("cybersecurity", "Cybersecurity Analyst", "EEGR 481", "Supports network security."),

    ("data", "Data Scientist/Analyst", "COSC 251", "Introduces data science skills."),
    ("data", "Data Scientist/Analyst", "COSC 472", "Directly supports machine learning."),
    ("data", "Data Scientist/Analyst", "MATH 331", "Builds probability and statistics foundation."),
    ("data", "Data Scientist/Analyst", "MATH 312", "Builds linear algebra foundation."),
    ("data", "Data Scientist/Analyst", "CLCO 471", "Supports cloud data analytics."),

    ("ai", "AI/Machine Learning Engineer", "COSC 470", "Directly supports artificial intelligence."),
    ("ai", "AI/Machine Learning Engineer", "COSC 472", "Directly supports machine learning."),
    ("ai", "AI/Machine Learning Engineer", "MATH 312", "Supports linear algebra for AI models."),
    ("ai", "AI/Machine Learning Engineer", "MATH 331", "Supports probability and statistics for AI."),
    ("ai", "AI/Machine Learning Engineer", "COSC 220", "Builds algorithms and data structures."),

    ("web", "Web Developer/Full-Stack Developer", "COSC 112", "Builds programming fundamentals."),
    ("web", "Web Developer/Full-Stack Developer", "COSC 220", "Builds backend logic skills."),
    ("web", "Web Developer/Full-Stack Developer", "COSC 458", "Supports software project development."),
    ("web", "Web Developer/Full-Stack Developer", "COSC 459", "Supports database-backed web apps."),
    ("web", "Web Developer/Full-Stack Developer", "COSC 238", "Supports object-oriented programming."),

    ("devops", "DevOps Engineer", "COSC 349", "Builds networking knowledge."),
    ("devops", "DevOps Engineer", "COSC 354", "Builds operating systems knowledge."),
    ("devops", "DevOps Engineer", "CLCO 261", "Introduces cloud computing."),
    ("devops", "DevOps Engineer", "CLCO 471", "Supports cloud data analytics."),
    ("devops", "DevOps Engineer", "COSC 458", "Supports software development workflows."),

    ("database", "Database Administrator", "COSC 459", "Directly supports database design."),
    ("database", "Database Administrator", "COSC 220", "Builds data structure fundamentals."),
    ("database", "Database Administrator", "COSC 458", "Supports software systems development."),

    ("qa", "Quality Assurance Analyst", "COSC 458", "Supports software testing and software engineering."),
    ("qa", "Quality Assurance Analyst", "COSC 112", "Builds programming fundamentals."),
    ("qa", "Quality Assurance Analyst", "COSC 220", "Builds logic and algorithm skills."),

    ("network", "Network Architect", "COSC 349", "Directly supports computer networking."),
    ("network", "Network Architect", "COSC 351", "Supports network security concepts."),
    ("network", "Network Architect", "EEGR 481", "Supports network security."),

    ("forensic", "Forensic Computer Analyst", "COSC 351", "Supports cybersecurity investigation skills."),
    ("forensic", "Forensic Computer Analyst", "COSC 323", "Supports cryptography knowledge."),
    ("forensic", "Forensic Computer Analyst", "INSS 391", "Supports IT infrastructure security."),
]

cursor.executemany("""
INSERT INTO career_course_recommendations
(career_keyword, career_title, course_code, reason)
VALUES (?, ?, ?, ?)
""", career_course_recommendations)

students = [
    ("Theo", "Hagan", "Fall 2026", "Computer Science", 3.2),
    ("John", "Doe", "Fall 2026", "Computer Science", 2.8),
]

cursor.executemany("""
INSERT INTO students (first_name, last_name, entry_term, major, gpa)
VALUES (?, ?, ?, ?, ?)
""", students)

conn.commit()
conn.close()

print("student_advisor.db created successfully")
