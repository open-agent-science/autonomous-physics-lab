#!/usr/bin/env python3
"""Decision-autonomy CLI (TASK-0952, policy v0 — dry-run only).

Subcommands:
  propose   render a new decision-packet skeleton from the template
  validate  check packets against policy/decision-autonomy.yaml (default-deny)
  list      list packets, optionally only those needing the maintainer
  apply     refuse in v0: the policy status is dry_run and no class may apply

The validator is the enforcement half of the self-modification guard: a
packet whose decision_type is not in the approved matrix FAILS validation —
an agent cannot invent a permissive category.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = REPO_ROOT / "policy" / "decision-autonomy.yaml"
TEMPLATE_PATH = REPO_ROOT / "decisions" / "DECISION-TEMPLATE.yaml"
DECISIONS_DIR = REPO_ROOT / "decisions"

REQUIRED_TOP_FIELDS = (
    "decision_id",
    "decision_type",
    "autonomy_class",
    "reversibility",
    "external_exposure",
    "artifact_impact",
    "recommended_action",
    "basis",
    "devils_advocate",
    "veto",
    "decision_record",
)
QUORUM_MEMBER_FIELDS = ("vote", "agent_id", "vendor", "agent_tool", "model_version", "session_id")
ADVOCATE_FIELDS = ("alternative_considered", "strongest_objection", "why_rejected", "escalation_required")


def load_policy() -> dict:
    return yaml.safe_load(POLICY_PATH.read_text(encoding="utf-8"))


def classify(policy: dict, decision_type: str) -> str | None:
    entry = policy["decision_types"].get(decision_type)
    return entry["class"] if entry else None


def validate_packet(packet: dict, policy: dict) -> list[str]:
    """Return a list of violations; empty list means the packet is valid."""
    errors: list[str] = []
    for field in REQUIRED_TOP_FIELDS:
        if field not in packet:
            errors.append(f"missing field: {field}")
    if errors:
        return errors

    dtype = packet["decision_type"]
    matrix_class = classify(policy, dtype)
    if matrix_class is None:
        errors.append(
            f"decision_type '{dtype}' is not in the approved matrix "
            f"(default-deny: unknown types are {policy['unknown_decision_type_default']}; "
            "extending the matrix is autonomy_policy_change = maintainer-only)"
        )
        return errors
    if packet["autonomy_class"] != matrix_class:
        errors.append(
            f"autonomy_class '{packet['autonomy_class']}' does not match the "
            f"matrix mapping '{matrix_class}' for decision_type '{dtype}'"
        )

    impact = packet["artifact_impact"]
    impactful = [k for k, v in impact.items() if v]
    if impactful and matrix_class != "class_2_maintainer_only":
        errors.append(
            f"artifact impact {impactful} requires class_2_maintainer_only, not {matrix_class}"
        )

    record = packet["decision_record"]
    if matrix_class == "class_2_maintainer_only" and record.get("decided_by") != "maintainer":
        errors.append("class_2 packets must have decision_record.decided_by: maintainer")

    if matrix_class == "class_1_lazy_consensus":
        quorum = packet.get("agent_quorum") or {}
        members = [v for v in quorum.values() if isinstance(v, dict)]
        rules = policy["autonomy_classes"]["class_1_lazy_consensus"]["quorum"]
        if len(members) < rules["min_votes"]:
            errors.append(f"class_1 requires >= {rules['min_votes']} quorum members")
        sessions = set()
        for member in members:
            for field in QUORUM_MEMBER_FIELDS:
                if not member.get(field):
                    errors.append(f"quorum member missing '{field}'")
            sessions.add(member.get("session_id"))
        if rules["separate_sessions_required"] and len(sessions) < len(members):
            errors.append("quorum members must come from separate sessions (distinct session_id)")
        advocate = packet["devils_advocate"]
        for field in ADVOCATE_FIELDS:
            if advocate.get(field) in (None, "", "..."):
                errors.append(f"devils_advocate.{field} must be filled")
        if advocate.get("escalation_required") is True and record.get("decided_by") != "maintainer":
            errors.append("devil's advocate found a blocker: escalation to maintainer is mandatory")
        if packet["veto"].get("window_hours") != rules.get("veto_window_hours", 48):
            errors.append("veto.window_hours must match the policy window")

    if policy["status"] == "dry_run":
        if record.get("status") not in ("dry_run_only", "vetoed") and record.get("decided_by") != "maintainer":
            errors.append("policy v0 is dry_run: agent packets must carry decision_record.status: dry_run_only")
        if record.get("applied_by") == "agent":
            errors.append("policy v0 is dry_run: applied_by: agent is forbidden")
    return errors


def cmd_propose(args: argparse.Namespace) -> int:
    policy = load_policy()
    matrix_class = classify(policy, args.type)
    if matrix_class is None:
        print(f"REFUSED: decision_type '{args.type}' is not in the approved matrix (default-deny).")
        return 1
    packet = yaml.safe_load(TEMPLATE_PATH.read_text(encoding="utf-8"))
    packet["decision_id"] = args.id
    packet["decision_type"] = args.type
    packet["autonomy_class"] = matrix_class
    out = DECISIONS_DIR / f"{args.id}.yaml"
    if out.exists():
        print(f"REFUSED: {out} already exists")
        return 1
    out.write_text(yaml.safe_dump(packet, sort_keys=False, allow_unicode=True), encoding="utf-8")
    print(f"proposed {out} (class: {matrix_class}; fill quorum, advocate, and basis before validate)")
    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    policy = load_policy()
    failed = 0
    for path in args.files:
        packet = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
        errors = validate_packet(packet, policy)
        if errors:
            failed += 1
            print(f"FAIL {path}")
            for error in errors:
                print(f"  - {error}")
        else:
            print(f"OK   {path}")
    return 1 if failed else 0


def cmd_list(args: argparse.Namespace) -> int:
    policy = load_policy()
    for path in sorted(DECISIONS_DIR.glob("DEC-*.yaml")):
        packet = yaml.safe_load(path.read_text(encoding="utf-8"))
        cls = packet.get("autonomy_class", "?")
        needs_maintainer = cls == "class_2_maintainer_only" or (
            packet.get("devils_advocate", {}).get("escalation_required") is True
        )
        if args.needs_maintainer and not needs_maintainer:
            continue
        status = packet.get("decision_record", {}).get("status", "?")
        print(f"{packet.get('decision_id', path.stem)}  [{cls}]  status={status}"
              f"{'  NEEDS-MAINTAINER' if needs_maintainer else ''}")
    _ = policy
    return 0


def cmd_apply(args: argparse.Namespace) -> int:
    policy = load_policy()
    if policy["status"] == "dry_run":
        print(
            "REFUSED: policy v0 is dry_run — no autonomy class may auto-apply. "
            "Enabling apply is an autonomy_policy_change (maintainer-only matrix edit)."
        )
        return 1
    print("REFUSED: apply is not implemented beyond dry-run in v0.")
    return 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("propose", help="render a packet skeleton from the template")
    p.add_argument("--id", required=True, help="decision id, e.g. DEC-20260707-frb-gate")
    p.add_argument("--type", required=True, help="decision_type from the approved matrix")
    p.set_defaults(func=cmd_propose)

    p = sub.add_parser("validate", help="validate decision packets")
    p.add_argument("files", nargs="+")
    p.set_defaults(func=cmd_validate)

    p = sub.add_parser("list", help="list decision packets")
    p.add_argument("--needs-maintainer", action="store_true")
    p.set_defaults(func=cmd_list)

    p = sub.add_parser("apply", help="apply a packet (always refuses in v0 dry-run)")
    p.add_argument("file")
    p.set_defaults(func=cmd_apply)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
