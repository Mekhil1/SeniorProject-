"""Narrow Networking patch audit and opt-in acceptance; no deployment calls."""
import ast
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
MANIFEST=ROOT/'tests/diagnostics/career_wave65_parity.json'
TARGET='networking__professional_communication_agent'
RULE='''

PLATFORM-SPECIFIC FACT BOUNDARY
On stable/no-retrieval guidance, do not state exact platform-specific limits, requirements, feature rules, pricing, allowances, account restrictions, or current product behavior (including LinkedIn connection-note/message limits, InMail allowances and recruiter/Premium features), unless explicitly supplied by the user; attribute those facts to the user, not independent verification. Say "Keep the connection note brief and personalized," not "Keep it under 300 characters." If an exact platform fact materially matters, retrieve and support it through the existing current-fact path or explicitly say it was not verified. An explicit request such as "What is LinkedIn's current connection-request note character limit?" qualifies for current-fact retrieval. Generic recruiter templates, outreach/follow-up strategy, tone, personalization and relationship-building remain useful and tool-free; do not search merely to enrich them.
'''


def sha(raw):return hashlib.sha256(raw).hexdigest()


def restore_before_patch(tree):
    """Strict historical-test normalization; never used by runtime agents."""
    from career_wave5 import nodes,instruction_value
    m=json.loads(MANIFEST.read_text(encoding='utf8'))
    node=nodes(tree)[TARGET]
    k=next(k for k in node.value.keywords if k.arg=='instruction')
    value=instruction_value(k.value)
    if sha(value.encode())==m['new_sha256']:
        assert isinstance(k.value,ast.BinOp) and isinstance(k.value.op,ast.Add)
        assert isinstance(k.value.right,ast.Constant) and k.value.right.value==RULE
        k.value=k.value.left
    assert sha(instruction_value(k.value).encode())==m['old_sha256'],'Unmeasured Networking instruction'
    return tree
