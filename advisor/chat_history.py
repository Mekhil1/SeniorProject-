"""Account-owned chat history and persistent Academic Advising sessions."""
from uuid import uuid4

from flask_login import current_user

from .secure_auth import connection

SERVICES = {"academic", "career", "tutoring", "success"}


class ConversationChanged(RuntimeError):
    """A concurrent request completed while an advising reply was generated."""


def runtime_user_id(fallback):
    return f"student-{current_user.id}" if current_user.is_authenticated else fallback


def save_exchange(service, question, result, expected_revision=None):
    if not current_user.is_authenticated:
        return
    with connection() as db:
        if expected_revision is not None:
            updated = db.execute(
                "UPDATE advising_sessions SET revision=revision+1 "
                "WHERE id=? AND user_id=? AND revision=?",
                (result["session_id"], current_user.id, expected_revision),
            )
            if updated.rowcount != 1:
                raise ConversationChanged()
        db.execute(
            "INSERT INTO chats (user_id,service,session_id,question,reply,created_at) "
            "VALUES (?,?,?,?,?,strftime('%s','now'))",
            (current_user.id, service, result.get("session_id"), question, result["reply"]),
        )


def advising_context(session_id):
    """Return an owned session, its revision, and up to twenty previous turns."""
    with connection() as db:
        if session_id is None:
            session_id = str(uuid4())
            db.execute("INSERT INTO advising_sessions (id,user_id) VALUES (?,?)",
                       (session_id, current_user.id))
        row = db.execute("SELECT revision FROM advising_sessions WHERE id=? AND user_id=?",
                         (session_id, current_user.id)).fetchone()
        if row is None:
            raise LookupError("Conversation is unavailable.")
        rows = db.execute(
            "SELECT question,reply FROM chats WHERE user_id=? AND service='academic' "
            "AND session_id=? ORDER BY id DESC LIMIT 20",
            (current_user.id, session_id),
        ).fetchall()
    return session_id, row["revision"], [dict(item) for item in reversed(rows)]
