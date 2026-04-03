# Whatagraph Claude Agent Skills

A collection of [Claude Agent Skills](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview) for the Whatagraph MCP server. These skills teach Claude how to effectively use Whatagraph's marketing analytics platform through the [Model Context Protocol](https://modelcontextprotocol.io/).

## Overview

Whatagraph is a marketing data platform that connects 50+ marketing channels (Google Ads, Meta, GA4, LinkedIn, TikTok, etc.) into unified reports, dashboards, and automated deliveries. The Whatagraph MCP server provides read-only access to all account data through structured tools.

These skills help Claude navigate the platform, fetch and interpret marketing data, analyze reports, troubleshoot issues, perform cross-channel comparisons, generate insights, and audit account health.

## Skills

| Skill | Description |
|-------|-------------|
| [exploring-account-data](skills/exploring-account-data/) | Navigate data sources, integrations, metrics, dimensions, spaces, and reports |
| [fetching-marketing-metrics](skills/fetching-marketing-metrics/) | Fetch raw performance data with proper metric/dimension selection and date ranges |
| [analyzing-reports](skills/analyzing-reports/) | Examine report structure, widgets, tabs, templates, themes, and sharing settings |
| [troubleshooting-data-issues](skills/troubleshooting-data-issues/) | Diagnose data discrepancies, source errors, blend issues, and filter problems |
| [cross-channel-analytics](skills/cross-channel-analytics/) | Analyze performance across channels using blends, source groups, and custom fields |
| [generating-marketing-insights](skills/generating-marketing-insights/) | Generate executive summaries, trend analysis, and actionable recommendations |
| [auditing-account-health](skills/auditing-account-health/) | Review source connections, automations, sharing, goals, and account configuration |

## Prerequisites

- Access to the [Whatagraph MCP server](https://mcp.whatagraph.com)
- A Whatagraph account with connected data sources
- Claude with MCP integration enabled

## Installation

### Claude Desktop / Claude.ai

1. Connect the Whatagraph MCP server to your Claude environment
2. Add the skills from this repository to your Claude skills directory:
   ```
   ~/.claude/skills/
   ```
3. Each skill folder contains a `SKILL.md` file that Claude loads when the skill is triggered

### Manual Installation

Copy the desired skill folders into your Claude skills directory:

```bash
cp -r skills/exploring-account-data ~/.claude/skills/
cp -r skills/fetching-marketing-metrics ~/.claude/skills/
# ... etc
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
