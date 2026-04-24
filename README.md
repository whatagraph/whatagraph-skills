# Whatagraph Claude Agent Skills

A collection of [Claude Agent Skills](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview) for the Whatagraph MCP server. These skills teach Claude how to effectively use Whatagraph's marketing analytics platform through the [Model Context Protocol](https://modelcontextprotocol.io/).

## Overview

Whatagraph is a marketing data platform that connects 60+ marketing channels (Google Ads, GA4, Shopify, Salesforce, Mailchimp, and more) into unified reports, dashboards, and automated deliveries. The Whatagraph MCP server provides read-only access to all account data through structured tools.

These skills help Claude navigate the platform, fetch and interpret marketing data, analyze reports, troubleshoot issues, perform cross-channel comparisons, generate insights, and audit account health.

## Skills

| Skill | Description |
|-------|-------------|
| [exploring-account-data](skills/exploring-account-data/) | Navigate data sources, integrations, metrics, dimensions, spaces, and reports |
| [fetching-marketing-metrics](skills/fetching-marketing-metrics/) | Fetch raw performance data with proper metric/dimension selection and date ranges |
| [generating-report-digests](skills/generating-report-digests/) | Summarize an existing Whatagraph report from a report URL, including comparison metrics and date-range overrides |
| [analyzing-reports](skills/analyzing-reports/) | Examine report structure, widgets, tabs, templates, themes, and sharing settings |
| [troubleshooting-data-issues](skills/troubleshooting-data-issues/) | Diagnose data discrepancies, source errors, blend issues, and filter problems |
| [cross-channel-analytics](skills/cross-channel-analytics/) | Analyze performance across channels using blends, source groups, and custom fields |
| [generating-marketing-insights](skills/generating-marketing-insights/) | Generate executive summaries, trend analysis, and actionable recommendations |
| [auditing-account-health](skills/auditing-account-health/) | Review source connections, automations, sharing, goals, and account configuration |

## Whatagraph MCP Server

These skills are designed to work with the **Whatagraph MCP server**:

- **Server info**: [https://mcp.whatagraph.com](https://mcp.whatagraph.com)
- **MCP endpoint**: `https://mcp.whatagraph.com/mcp`

The MCP server provides read-only access to your Whatagraph account data — sources, reports, widgets, metrics, and more. To connect, add the server endpoint to your MCP client configuration using your Whatagraph API credentials.

## Prerequisites

- A Whatagraph account with connected data sources
- Claude with MCP integration enabled
- The Whatagraph MCP server connected at `https://mcp.whatagraph.com/mcp`

## Installation

First, connect the Whatagraph MCP server (`https://mcp.whatagraph.com/mcp`) to your Claude environment, then install the skills using one of the options below.

### Option 1 — One-line install (Claude Code / Claude Desktop, macOS & Linux)

Copies every skill folder (with its `SKILL.md` inside) directly into `~/.claude/skills/`, keeping the original folder names. No `git` required.

```bash
mkdir -p ~/.claude/skills && \
  curl -L https://github.com/whatagraph/whatagraph-skills/archive/refs/heads/main.tar.gz | \
  tar -xz -C ~/.claude/skills --strip-components=2 whatagraph-skills-main/skills
```

Re-run the command any time to update to the latest version — `tar` will overwrite the existing files.

To install only specific skills, append the skill paths to the `tar` command, for example:

```bash
mkdir -p ~/.claude/skills && \
  curl -L https://github.com/whatagraph/whatagraph-skills/archive/refs/heads/main.tar.gz | \
  tar -xz -C ~/.claude/skills --strip-components=2 \
  whatagraph-skills-main/skills/fetching-marketing-metrics \
  whatagraph-skills-main/skills/generating-report-digests
```

### Option 2 — Git clone + symlink (keeps skills updatable via `git pull`)

```bash
git clone https://github.com/whatagraph/whatagraph-skills.git ~/whatagraph-skills
mkdir -p ~/.claude/skills
ln -s ~/whatagraph-skills/skills/* ~/.claude/skills/
```

Later, update all skills with a single command:

```bash
git -C ~/whatagraph-skills pull
```

### Option 3 — Claude.ai web (packaged zips for upload)

The Claude.ai web interface uploads one `.zip` per skill. Run the packaging script to produce one zip per skill under `dist/`:

```bash
git clone https://github.com/whatagraph/whatagraph-skills.git
cd whatagraph-skills
./scripts/package-skills.sh
```

This creates `dist/exploring-account-data.zip`, `dist/fetching-marketing-metrics.zip`, etc. — drag each one into the Skills section of your Claude.ai workspace settings.

### Option 4 — Ask your coding agent to install them

If you use an agent with shell access (Claude Code, Cursor, Devin, etc.), paste the following prompt and it will install the skills for you:

> Please install the Whatagraph Claude Agent Skills from <https://github.com/whatagraph/whatagraph-skills>.
>
> 1. Create `~/.claude/skills/` if it doesn't exist.
> 2. Download the latest `main` archive and extract every folder from `skills/` into `~/.claude/skills/`, preserving the original folder names (each skill is a directory containing a `SKILL.md`).
> 3. List the installed skills under `~/.claude/skills/` and confirm each one has a `SKILL.md` inside.
> 4. If any skill already exists locally, overwrite it with the latest version.
>
> A one-liner that does steps 1–2 on macOS/Linux is:
>
> ```bash
> mkdir -p ~/.claude/skills && \
>   curl -L https://github.com/whatagraph/whatagraph-skills/archive/refs/heads/main.tar.gz | \
>   tar -xz -C ~/.claude/skills --strip-components=2 whatagraph-skills-main/skills
> ```

### Option 5 — Manual copy (if you only want one or two)

```bash
git clone https://github.com/whatagraph/whatagraph-skills.git
cp -r whatagraph-skills/skills/generating-report-digests ~/.claude/skills/
```

## MCP Tools Reference

These skills leverage the following Whatagraph MCP tools:

| Tool | Purpose |
|------|---------|
| `list-sources` | Browse and inspect connected data sources |
| `fetch-data` | Retrieve marketing performance data |
| `list-spaces` | Navigate client/project folders |
| `list-reports` | Browse reports |
| `list-report-tabs` | Browse tabs within reports |
| `list-widgets` | Inspect widget configurations and export data |
| `export-report` | Export all widgets in a report in one call (with comparison metrics) |
| `list-integrations` | Browse connected channels and accounts |
| `list-themes` | Review report visual themes |
| `list-templates` | Browse report templates |
| `list-snapshots` | Browse saved report versions |
| `view-sharing` | Check report sharing settings |
| `view-team` | View team settings and global search |
| `list-automations` | Review scheduled report deliveries |
| `list-custom-metrics` | Browse user-created metrics |
| `list-custom-dimensions` | Browse user-created dimensions |
| `list-blends` | Browse cross-channel data blends |
| `list-source-groups` | Browse aggregated source groups |
| `list-filters` | Browse saved filters |
| `list-overviews` | Browse KPI tracking dashboards |
| `view-goals` | View performance targets |

## Contributing

Contributions are welcome. Please open an issue or pull request.

## License

This project is licensed under the Apache License 2.0. See [LICENSE](LICENSE) for details.
