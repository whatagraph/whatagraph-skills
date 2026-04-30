# Whatagraph Agent Skills

A collection of [Agent Skills](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview) for the Whatagraph MCP server. These skills teach an AI agent how to use Whatagraph's marketing analytics platform through the [Model Context Protocol](https://modelcontextprotocol.io/).

## Overview

Whatagraph is a marketing data platform that connects 60+ marketing channels (Google Ads, GA4, Shopify, Salesforce, Mailchimp, and more) into unified reports, dashboards, and automated deliveries. The Whatagraph MCP server exposes the platform so an agent can browse connected data sources, fetch data, and — where enabled — build and maintain reports, source groups, blends, custom metrics and dimensions, measurements, goals, sharing, automations, and more.

These skills teach agents how to use each part of the platform the way customers actually use it — end to end, reliably, in one shot.

## Skills

### Domain skills (one per area of the product)

| Skill | What it covers |
|-------|----------------|
| [whatagraph-mcp-overview](skills/whatagraph-mcp-overview/) | Start here. How the tools fit together, common decision trees, and which skill to load for which request |
| [whatagraph-customer-patterns](skills/whatagraph-customer-patterns/) | End-to-end multi-tool flows: onboarding a new client, cross-channel paid media, debugging data mismatches, rebranding at scale |
| [whatagraph-spaces](skills/whatagraph-spaces/) | Create and manage spaces (client folders) — the top-level container for reports and data |
| [whatagraph-sources-and-data](skills/whatagraph-sources-and-data/) | Discover sources, list their metrics/dimensions, fetch raw data, tag, set currency |
| [whatagraph-integrations-admin](skills/whatagraph-integrations-admin/) | Browse integrations, add sources from connected accounts, assign sources to spaces |
| [whatagraph-source-groups](skills/whatagraph-source-groups/) | Combine multiple sources of the same channel into one virtual aggregated source |
| [whatagraph-blends](skills/whatagraph-blends/) | Join data from different channels on shared dimensions into one virtual source |
| [whatagraph-custom-metrics](skills/whatagraph-custom-metrics/) | Build formula, aggregation, and currency-converted metrics on top of sources, groups, and blends |
| [whatagraph-custom-dimensions](skills/whatagraph-custom-dimensions/) | Build tag dimensions, formula dimensions, and cross-source unified dimensions |
| [whatagraph-filters](skills/whatagraph-filters/) | Create and apply reusable filter configs on sources, blends, and widgets |
| [whatagraph-reports](skills/whatagraph-reports/) | Create, duplicate, update reports; apply templates; bulk-swap data sources |
| [whatagraph-report-tabs](skills/whatagraph-report-tabs/) | Create, duplicate, reorder, and rename tabs; move widgets between tabs |
| [whatagraph-widgets](skills/whatagraph-widgets/) | Create, configure, duplicate widgets; sizing rules; batch source and field swaps |
| [whatagraph-templates](skills/whatagraph-templates/) | Convert reports into linked templates and apply them to new reports |
| [whatagraph-themes](skills/whatagraph-themes/) | Apply themes and color palettes for client branding |
| [whatagraph-overviews](skills/whatagraph-overviews/) | Build single-page KPI dashboards (Measurements) |
| [whatagraph-goals](skills/whatagraph-goals/) | Set performance targets on metrics and track progress |
| [whatagraph-sharing](skills/whatagraph-sharing/) | Create share links, generate PDFs, export to Excel |
| [whatagraph-automations](skills/whatagraph-automations/) | Schedule recurring PDF/email deliveries |
| [whatagraph-snapshots](skills/whatagraph-snapshots/) | Save and restore report structure |
| [whatagraph-export](skills/whatagraph-export/) | Bulk-export report, tab, or widgets to CSV |
| [whatagraph-destinations](skills/whatagraph-destinations/) | View data pushes to external destinations (BigQuery, Looker Studio, etc.) |
| [whatagraph-team-and-members](skills/whatagraph-team-and-members/) | View team settings, invite members, manage roles |

### Task skills

The task-oriented skills (`exploring-account-data`, `fetching-marketing-metrics`, `generating-report-digests`, `analyzing-reports`, `troubleshooting-data-issues`, `cross-channel-analytics`, `generating-marketing-insights`, `auditing-account-health`) remain in the repo — they compose the domain skills above for higher-level workflows.

## Connecting the MCP server

- Server info: [https://mcp.whatagraph.com](https://mcp.whatagraph.com)
- MCP endpoint: `https://mcp.whatagraph.com/mcp`

Add the server endpoint to your MCP client with your Whatagraph API credentials. Once connected, any agent using these skills will be able to call the Whatagraph tools directly.

## Tool availability

Read tools (browsing data, fetching metrics, exporting reports) are available on all plans.

**Write and delete tools (creating, updating, or deleting reports, widgets, source groups, blends, custom metrics and dimensions, goals, sharing, automations, etc.) are currently in a private alpha** and only enabled for a selected set of customers. The skills describe the full surface — if a tool isn't enabled for your team, the server will return an error and the agent will fall back to read-only behavior.

To request alpha access, reach out to Whatagraph support.

## Prerequisites

- A Whatagraph account with at least one connected data source.
- An MCP-enabled AI environment (Claude Code, Claude Desktop, Cursor, and similar).
- The Whatagraph MCP server connected at `https://mcp.whatagraph.com/mcp`.

## Installation

Pick whichever path matches your environment.

### Ask your agent to install them (no terminal needed)

If you use an agent with shell access (Claude Code, Cursor, etc.), paste the following prompt:

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

```bash
git clone https://github.com/whatagraph/whatagraph-skills.git
cp -r whatagraph-skills/skills/* ~/.claude/skills/
```

To install a subset, copy only the folders you want:

```bash
cp -r whatagraph-skills/skills/generating-report-digests ~/.claude/skills/
```

To stay on the latest version, symlink instead of copying:

```bash
git clone https://github.com/whatagraph/whatagraph-skills.git ~/whatagraph-skills
mkdir -p ~/.claude/skills
ln -s ~/whatagraph-skills/skills/* ~/.claude/skills/
git -C ~/whatagraph-skills pull   # run later to update
```

### Claude.ai web

The Claude.ai web UI uploads one `.zip` per skill:

```bash
git clone https://github.com/whatagraph/whatagraph-skills.git
cd whatagraph-skills/skills
for dir in */; do (cd "$dir" && zip -r "../../${dir%/}.zip" .); done
```

Drag each generated `.zip` into the Skills section of your Claude.ai workspace settings.

## What the skills cover

Every tool the Whatagraph MCP server exposes is covered — reading data, browsing metrics, fetching rows, exporting reports, and (where enabled) creating, updating, and deleting the assets that make up a Whatagraph account.

Areas include: sources and data, integrations, spaces, reports, tabs, widgets, source groups, blends, custom metrics, custom dimensions, filters, measurements (overviews), goals, templates, themes, sharing (public links, PDF, Excel), automations, snapshots, bulk CSV export, destinations, team and members.

## Contributing

Issues and pull requests are welcome.

## License

Apache License 2.0. See [LICENSE](LICENSE) for details.
