"""Wave 2 canaries using the existing sanitized local-workflow observer.

Default invocation only prints the plan. Run one --case at a time with --live;
never retry a 429-affected case. No Agent Engine or deployment calls.
"""
import argparse
import asyncio
import json
from pathlib import Path

import career_baseline as baseline


def plan():
    existing = {c["id"]: c for c in baseline.plan()}
    current = [
        ("certification", "What is the current CompTIA Security+ exam version and price?"),
        ("networking", "What current networking resources can Morgan State Computer Science students use?"),
        ("research", "What current cybersecurity research opportunities are available at Morgan State?"),
        ("interview", "What is the current interview process for an entry-level cybersecurity role at Microsoft?"),
    ]
    cases = []
    for domain, prompt in current:
        case = dict(existing[domain + "_current_1"])
        case.update(id="wave2_" + domain + "_current", prompt=prompt)
        cases.append(case)
    for domain, _ in current:
        case = dict(existing[domain + "_stable_1"])
        case.update(id="wave2_" + domain + "_stable")
        if domain == "research":
            case["prompt"] = "What are the general steps to prepare for graduate cybersecurity research? Focus on research readiness, not current programs."
        cases.append(case)
    return cases


def cli():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--case", action="append", choices=[c["id"] for c in plan()])
    parser.add_argument("--output", type=Path, default=baseline.ROOT / "tests/diagnostics/career_wave2.json")
    parser.add_argument("--timeout", type=float, default=180)
    parser.add_argument("--pace", type=float, default=20)
    args = parser.parse_args()
    if not args.live:
        print(json.dumps(plan(), indent=2))
        return
    if not args.case or len(args.case) != 1:
        parser.error("Live Wave 2 execution requires exactly one --case; review it before the next.")
    if args.output.exists() and not args.resume:
        parser.error("Output exists; use --resume to retain previous attempts.")
    asyncio.run(baseline.main_async(args, cases_override=plan()))


if __name__ == "__main__":
    cli()
