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

First, connect the Whatagraph MCP server (`https://mcp.whatagraph.com/mcp`) to your Claude environment, then install the skills.

### Ask your coding agent to install them (no terminal needed)

If you use an agent with shell access (Claude Code, Cursor, Devin, Codex, etc.), paste the prompt below into your agent. It will figure out the correct skills directory for your environment and install everything.

```
Please install the Whatagraph Agent Skills from https://github.com/whatagraph/whatagraph-skills.

1. Determine the correct skills directory for the agent/environment you are running in
   (e.g. ~/.claude/skills for Claude Code / Claude Desktop). If you are unsure, ask me.
2. Clone https://github.com/whatagraph/whatagraph-skills.git and copy every folder under
   its skills/ directory into the skills directory from step 1, preserving the folder
   names (each skill is a directory containing a SKILL.md file).
3. If any skills already exist locally, overwrite them with the latest version.
4. List the installed skill folders and confirm each contains a SKILL.md.
```

### Claude Code / Claude Desktop (terminal)

Clone the repo and copy the skills into your Claude skills directory:

```bash
git clone https://github.com/whatagraph/whatagraph-skills.git
cp -r whatagraph-skills/skills/* ~/.claude/skills/
```

To install a subset, copy only the folders you want (e.g. `cp -r whatagraph-skills/skills/generating-report-digests ~/.claude/skills/`).

If you'd rather pull updates later with `git pull`, symlink instead of copying:

```bash
git clone https://github.com/whatagraph/whatagraph-skills.git ~/whatagraph-skills
mkdir -p ~/.claude/skills
ln -s ~/whatagraph-skills/skills/* ~/.claude/skills/
git -C ~/whatagraph-skills pull   # run later to update
```

### Claude.ai web

The Claude.ai web UI uploads one `.zip` per skill. Clone the repo and zip each skill folder:

```bash
git clone https://github.com/whatagraph/whatagraph-skills.git
cd whatagraph-skills/skills
for dir in */; do (cd "$dir" && zip -r "../../${dir%/}.zip" .); done
```

Then drag each generated `.zip` into the Skills section of your Claude.ai workspace settings.

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
