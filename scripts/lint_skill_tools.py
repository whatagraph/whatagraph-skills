#!/usr/bin/env python3
"""Lint skill frontmatter tool lists against the tool inventory and skill bodies.

Rules enforced (per the agent-skill-permissions plan, section 1):
  1. Every tool the skill BODY invokes must appear in `required_tools`
     (CORE) or `optional_tools`.
  2. No unknown tool names in either list (validated against the canonical
     Whatagraph MCP tool inventory below).
  3. No tool appears in both `required_tools` and `optional_tools`.
  4. No DESTRUCTIVE tool (`delete-*`, `remove-integrations`, `remove-members`)
     appears in `required_tools` — except the `whatagraph-deleting` skill, whose
     happy path is deletion. Destructive tools gate a skill behind a permission
     the grant flow never auto-grants, making the skill unreachable; they belong
     in `optional_tools` (or dropped) for every domain skill.
  5. `group`, when declared, is one of the seven agreed functional categories.
     The key is OPTIONAL: read/analysis workflow skills and the orientation meta
     skills intentionally carry no group, and an absent key is not an error. Only
     a group that does not exist in the taxonomy is, since it would silently fail
     to match anything the frontend groups by.

`optional_tools` entries may be either a bare string or a mapping with a
`tool_name` key (and an optional `purpose`). `optional_tools` is optional; an
absent list is treated as empty (identical to today's behaviour).

A tool is treated as body-invoked when a call to it is actually shown: inside a
fenced code block (```) or an inline-code span, a line begins with the tool name
(optionally indented) immediately followed by an argument — `action=`,
`action:`, `source_id=`, `report_id=`, etc. This is the syntax every skill uses
to document a real call.

Prose cross-references ("load the `whatagraph-deleting` skill"), decision-tree
diagrams that mention a tool mid-sentence ("...via `manage-widgets` options"),
and "see also" pointers do not match this shape and are intentionally not
treated as invocations — a `type: meta` skill can legitimately reference many
tools while declaring none. Matching against the canonical inventory
additionally keeps tokens like "delete-and-recreate" or "read-only" from being
mistaken for a tool.

Exit status is non-zero when any skill violates a rule.
"""
from __future__ import annotations

import glob
import os
import re
import sys

# Canonical Whatagraph MCP tool inventory — the single source of truth for valid
# tool names. Generated from the backend, NOT hand-edited:
#
#   php artisan tinker --execute 'echo implode("\n", \
#     App\Domain\MCP\WhatagraphServer::allCanonicalToolNames());'
#
# Regenerate after any tool is added, renamed, or removed in whatagraph-api-v7.
# Drift is silent in both directions: a stale name passes lint but logs
# "skill declares unknown tools" at sync time and never gates anything, while a
# missing name fails lint for a tool that is perfectly real.
CANONICAL_TOOLS = {
    "list-agent-tools",
    "list-agents", "manage-agents", "delete-agents",
    "list-assets", "manage-assets",
    "list-automations", "manage-automations", "delete-automations",
    "list-blends", "manage-blends", "delete-blends",
    "list-conversations", "manage-conversations", "delete-conversations",
    "list-custom-dimensions", "manage-custom-dimensions", "delete-custom-dimensions",
    "list-custom-metrics", "manage-custom-metrics", "delete-custom-metrics",
    "list-destinations", "manage-destinations", "delete-destinations",
    "export-report",
    "list-external-connectors",
    "fetch-data",
    "list-filters", "manage-filters", "delete-filters",
    "manage-goals", "view-goals", "delete-goals",
    "list-integrations", "manage-integrations", "remove-integrations",
    "load-skill",
    "manage-members", "remove-members",
    "list-overviews", "manage-overviews", "delete-overviews",
    "read-document",
    "list-report-tabs", "manage-report-tabs", "delete-report-tabs",
    "list-reports", "manage-reports", "delete-reports",
    "search-assets",
    "manage-sharing", "view-sharing", "delete-sharing",
    "list-skills",
    "list-snapshots", "manage-snapshots", "delete-snapshots",
    "list-source-groups", "manage-source-groups", "delete-source-groups",
    "list-sources", "manage-sources", "delete-sources",
    "list-spaces", "manage-spaces", "delete-spaces",
    "manage-team", "view-team",
    "list-templates", "manage-templates", "delete-templates",
    "list-themes", "manage-themes", "delete-themes",
    "list-widgets", "manage-widgets", "delete-widgets",
}

# Destructive tools must never be CORE (`required_tools`) of a domain skill:
# every `delete-*` name plus the two `remove-*` tools. The grant flow never
# auto-grants these, so a skill that requires one is unreachable.
DESTRUCTIVE_TOOLS = {t for t in CANONICAL_TOOLS if t.startswith("delete-")} | {
    "remove-integrations",
    "remove-members",
}

# Skills exempt from Rule 4 — deletion is their happy path.
DESTRUCTIVE_CORE_EXEMPT = {"whatagraph-deleting"}

# Valid `group:` values. Must stay in sync with the backend's
# App\Domain\Agent\Enums\AgentToolGroup cases (minus `custom`, which is the
# registry's fallback bucket for an unannotated tool, never an authored value).
VALID_GROUPS = {
    "data_modeling",
    "data_connections",
    "report_building",
    "monitoring_kpis",
    "distribution_lifecycle",
    "team_workspace_branding",
    "deletion",
}


def split_frontmatter(text: str):
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
    if not m:
        return None, text
    return m.group(1), m.group(2)


def parse_scalar(frontmatter: str, key: str):
    """Return the scalar value declared under `key`, or None when absent."""
    m = re.search(rf"^{key}:[ \t]*(\S.*?)\s*$", frontmatter, re.M)
    return m.group(1) if m else None


def parse_tool_list(frontmatter: str, key: str):
    """Return the list of tool names declared under `key` in the frontmatter."""
    tools = []
    in_block = False
    for line in frontmatter.splitlines():
        if re.match(rf"^{key}:\s*$", line):
            in_block = True
            continue
        # A new top-level key ends the block.
        if in_block and re.match(r"^[A-Za-z_]", line):
            break
        if in_block:
            m = re.match(r"^\s*-\s*(?:tool_name:\s*)?([a-z][a-z0-9-]+)\s*$", line)
            if m:
                tools.append(m.group(1))
    return tools


def _call_context_lines(body: str):
    """Yield individual lines drawn from where calls are shown: fenced code
    blocks and inline-code spans."""
    # Fenced code blocks (``` ... ```), regardless of language hint.
    for m in re.finditer(r"```.*?\n(.*?)```", body, re.S):
        yield from m.group(1).splitlines()

    # Inline code spans (each is a candidate single-line call).
    body_no_fences = re.sub(r"```.*?```", "", body, flags=re.S)
    for m in re.finditer(r"`([^`]*)`", body_no_fences):
        yield m.group(1)


# A call line: tool name at the start (optionally indented / commented) followed
# by an argument such as `action=`, `action:`, `source_id=`, `report_id=`.
_CALL_RE = re.compile(r"^\s*#?\s*([a-z][a-z0-9-]+)[ \t]+[a-z_]+\s*[=:]")


def find_body_tools(body: str):
    found = set()
    for line in _call_context_lines(body):
        m = _CALL_RE.match(line)
        if m and m.group(1) in CANONICAL_TOOLS:
            found.add(m.group(1))
    return found


def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    errors = []
    files = sorted(glob.glob(os.path.join(root, "skills", "*", "SKILL.md")))
    if not files:
        print("No skills found — nothing to lint.", file=sys.stderr)
        return 1

    for path in files:
        rel = os.path.relpath(path, root)
        text = open(path, encoding="utf-8").read()
        fm, body = split_frontmatter(text)
        if fm is None:
            errors.append(f"{rel}: missing YAML frontmatter")
            continue

        required = parse_tool_list(fm, "required_tools")
        optional = parse_tool_list(fm, "optional_tools")
        req_set, opt_set = set(required), set(optional)
        declared = req_set | opt_set

        # Rule 2: unknown names.
        for name in sorted(declared):
            if name not in CANONICAL_TOOLS:
                errors.append(f"{rel}: unknown tool '{name}' (not in the MCP tool inventory)")

        # Rule 3: no tool in both lists.
        for name in sorted(req_set & opt_set):
            errors.append(f"{rel}: tool '{name}' is in both required_tools and optional_tools")

        # Rule 4: no destructive tool in required_tools (except deletion skills).
        skill_name = os.path.basename(os.path.dirname(path))
        if skill_name not in DESTRUCTIVE_CORE_EXEMPT:
            for name in sorted(req_set & DESTRUCTIVE_TOOLS):
                errors.append(
                    f"{rel}: destructive tool '{name}' must not be in required_tools "
                    f"(move it to optional_tools or drop it)"
                )

        # Rule 5: a declared group must exist in the taxonomy (absent is fine).
        group = parse_scalar(fm, "group")
        if group is not None and group not in VALID_GROUPS:
            errors.append(
                f"{rel}: unknown group '{group}' (expected one of: "
                f"{', '.join(sorted(VALID_GROUPS))})"
            )

        # Rule 1: body-invoked tools must be declared.
        body_tools = find_body_tools(body)
        for name in sorted(body_tools - declared):
            errors.append(
                f"{rel}: tool '{name}' is invoked in the body but is in neither "
                f"required_tools nor optional_tools"
            )

    if errors:
        print("Skill tool-list lint FAILED:\n", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        print(f"\n{len(errors)} problem(s) found.", file=sys.stderr)
        return 1

    print(f"Skill tool-list lint passed ({len(files)} skills checked).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
