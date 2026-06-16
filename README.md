# Whatagraph Agent Skills

Source repository for the [Agent Skills](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview) served by the [Whatagraph MCP server](https://mcp.whatagraph.com/).

Skills are short markdown playbooks loaded by the MCP server on demand via its `list-skills` / `load-skill` tools — there is no separate install step. They guide a discovery-first workflow: find sources, check available fields, then read, analyze, and (where enabled) build on your marketing data.

## Availability

> **Beta:** The **read & analysis** skills work against the generally available read-only tools. The **configure, manage & delete** skills correspond to write capabilities that are currently in **beta rollout** and are being enabled for accounts progressively — if a related tool isn't available for your account yet, the read skills still work, and the write skills will activate as the capability reaches your account.

## Skills

Start with `whatagraph-mcp-overview`; it explains the mental model (spaces → reports → tabs → widgets; data sources, source groups, blends) and routes to the rest.

### Read & analyze

| Skill | What it does |
|---|---|
| `whatagraph-mcp-overview` | Orientation and routing across all skills. Read first. |
| `exploring-account-data` | Discover what's connected — sources, integrations, report types, available metrics and dimensions, spaces and reports. |
| `fetching-marketing-metrics` | Fetch raw marketing performance numbers from any connected source via `fetch-data`. |
| `whatagraph-sources-and-data` | Discover data sources and the source/field reference, and pull raw numbers — use before any reporting task. |
| `analyzing-reports` | Examine an existing report's structure — widgets, tabs, templates, themes, sharing, snapshots, automations. |
| `cross-channel-analytics` | Compare performance across channels using blends, source groups, and custom metrics/dimensions. |
| `auditing-account-health` | Review account health — source connections, integration status, schedules, sharing, goals, subscription. |
| `generating-marketing-insights` | Turn data into executive summaries, trend analysis, narratives, and recommendations. |
| `generating-report-digests` | Produce a digest or summary of an existing report from a report URL or ID. |
| `troubleshooting-data-issues` | Diagnose data discrepancies, source connection problems, blend/source-group/filter issues, and missing data. |
| `whatagraph-export` | Export a whole report, a single tab, or specific widgets as CSV. |
| `whatagraph-destinations` | Inspect configured outbound data transfers (BigQuery, Looker Studio, storage) and their job history. |

### Configure, manage & delete (beta)

| Skill | What it does |
|---|---|
| `whatagraph-spaces` | Create and manage spaces (client folders). |
| `whatagraph-reports` | Create, duplicate, and update reports. |
| `whatagraph-report-tabs` | Create, duplicate, rename, and reorder report tabs. |
| `whatagraph-widgets` | Build and lay out widgets on the grid. |
| `whatagraph-blends` | Combine data from different channels into one virtual source. |
| `whatagraph-source-groups` | Roll up multiple accounts of the same channel into one aggregated source. |
| `whatagraph-custom-metrics` | Create calculated or unified metrics across sources. |
| `whatagraph-custom-dimensions` | Create derived dimensions — tag-based, condition-based, or AI-classified groupings. |
| `whatagraph-filters` | Create reusable saved filter configurations for a channel. |
| `whatagraph-overviews` | Create overviews — KPI dashboards (called "Measurements" in the UI). |
| `whatagraph-goals` | Create goals — metric targets with a deadline. |
| `whatagraph-templates` | Convert a report into a reusable template and apply templates to new reports. |
| `whatagraph-themes` | Apply and manage themes (logos, fonts, headers/footers) and color palettes. |
| `whatagraph-sharing` | Create and update public share links, generate PDFs, and export reports. |
| `whatagraph-automations` | Schedule automated report delivery by email. |
| `whatagraph-snapshots` | Save and restore the structural state of a report. |
| `whatagraph-integrations-admin` | Connect sources from already-authenticated accounts and assign them to spaces. |
| `whatagraph-team-and-members` | View team settings and subscription; invite and update team members. |
| `whatagraph-customer-patterns` | Common multi-tool flows and decision trees across skills. |
| `whatagraph-deleting` | Safe deletion, removal, and revocation across Whatagraph entities. |

## License

Apache License 2.0. See [LICENSE](LICENSE) for details.
