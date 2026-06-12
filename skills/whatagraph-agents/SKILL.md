---
name: whatagraph-agents
description: Build and operate custom AI agents (IQ Chats) via MCP — discover the agent tool catalog, create and edit agents with per-tool permissions, and start, follow, and cancel agent conversations. Covers the draft model for edits, tools_mode semantics (patch vs deny_unlisted), permission levels, and conversation lifecycle statuses.
required_tools:
  - list-agent-tools
  - list-agents
  - list-user-conversations
  - create-agent
  - edit-agent
  - manage-user-conversations
---

# Agents (IQ Chats)

Tools covered: `list-agent-tools`, `list-agents`, `list-user-conversations`, `create-agent`, `edit-agent`, `manage-user-conversations`.

An **agent** is a team-scoped AI assistant with its own instructions (system prompt), model, reasoning depth, per-turn step budget, and per-tool permissions. Conversations are routed to an agent by a classifier that reads the agent's `description` — write descriptions for the router, not for humans.

These tools are served only on environments where the agent platform is enabled (they are not exposed on production). If they are absent from the tool list, this skill does not apply.

## Use this when

- The user wants a purpose-built assistant ("an agent that audits our Google Ads spend weekly").
- The user wants to change what an existing agent may do (tools, permissions, model, step budget).
- The user wants to start, monitor, or cancel a conversation with an agent.

## Discover the tool catalog first

```
list-agent-tools search=<term> category=<read|write|destructive>
```

Returns each tool's canonical `tool_name`, `title`, `category`, `default_permission`, and description. **Pass `tool_name` values verbatim into `create-agent`/`edit-agent` — never invent or snake_case them.** Registry defaults: read-only tools are `always_allow`, write tools are `needs_approval`.

## Create an agent

```
create-agent name=<name> description=<routing description> instructions=<system prompt> model=<model> max_steps=<n> tools=[{"tool_name": "<from list-agent-tools>", "permission": "always_allow"}] tools_mode=deny_unlisted
```

- `name` and `description` are the only required fields. The agent starts active.
- `tools_mode` decides what happens to tools you did NOT list: `patch` (default) leaves them at registry defaults; `deny_unlisted` forces them to `denied`. When the user says "only X" / "just X" / "restrict to X", use `deny_unlisted` — with `patch`, every unlisted tool stays available at its default.
- `max_steps` (1–254, default 100) is the per-turn tool-call budget, not a loop guard — size it to the heaviest workflow the agent will run. Loops are caught independently by the platform.
- `thinking_level` (`minimal`/`low`/`medium`/`high`) is model-specific; unsupported levels are rejected or clamped (verified Jun 2026).

## Edit an agent — drafts, not live changes

```
edit-agent agent_ulid=<ulid> instructions=<new prompt> tools=[...] tools_mode=patch
```

> **Warning:** `edit-agent` writes to a **draft** — the live agent is unchanged until the user explicitly saves the draft in the UI. Tell the user their changes are staged, not live. Only one draft per agent exists; if another conversation already holds one, the edit fails with a `draft_conflict` error — that draft must be saved or discarded first.

Find `agent_ulid` via `list-agents action=list`; `list-agents action=show agent_ulid=<ulid>` returns full tool permissions and draft status.

## Run conversations

```
manage-user-conversations action=create message=<text> agent_ulid=<optional ulid>
manage-user-conversations action=send_message conversation_id=<ulid> message=<text>
manage-user-conversations action=cancel conversation_id=<ulid>
list-user-conversations action=list filter_status=<status>
list-user-conversations action=show conversation_id=<ulid>
```

- Omitting `agent_ulid` on `create` lets the classifier pick the agent from the message.
- Conversation statuses: `active`, `processing`, `retrying`, `idle`, `cancelling`, `cancelled`, `requires_action`, `failed`, `completed`, `archived`. A long-running build sits in `processing`; poll with `show` rather than re-sending the message — a re-send starts another turn.
- `show` returns the full message snapshot, including tool calls and results.

## What MCP can't do here

- Save or discard an agent draft — the user does that in the UI.
- Delete an agent — no delete tool exists for agents.
- Change which tools the platform itself can offer (`list-agent-tools` is the fixed catalog).

## Common pitfalls

- **Inventing tool names** — `tools[].tool_name` must come from `list-agent-tools` verbatim; unknown names are rejected or silently useless.
- **Using `patch` for "only these tools"** — `patch` leaves every unlisted tool at its registry default, so the agent keeps broad access. Use `deny_unlisted` for restriction requests.
- **Granting `always_allow` on write/destructive tools by default** — keep registry defaults unless the user explicitly accepts the risk; an agent with blanket `always_allow` can modify or delete team assets unattended.
- **Treating `needs_approval` as a working approval flow** — currently a `needs_approval` tool is simply not available to the agent at run time; there is no interactive approval round-trip yet (verified Jun 2026). If the agent must use a tool, it needs `always_allow`; say so to the user instead of promising an approval prompt.
- **Expecting `edit-agent` to change live behavior immediately** — it stages a draft; the live agent answers with the old configuration until the draft is saved.
- **Re-sending the first message when a conversation is `processing`** — that queues a second turn; poll `list-user-conversations action=show` instead.
