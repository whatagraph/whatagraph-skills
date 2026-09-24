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
| `whatagraph-export` | Export a report as a PDF or Excel/CSV, preview its pages as images to check how it renders, or view the actual ad-creative images from its media widgets for creative analysis. |
| `whatagraph-destinations` | Create outbound data transfers (BigQuery, Looker Studio, storage), inspect the configured ones and their job history, and control them. |

### Configure, manage & delete (beta)

| Skill | What it does |
|---|---|
| `whatagraph-spaces` | Create and manage spaces (client folders). |
| `whatagraph-reports` | Create, duplicate, and update reports. |
| `whatagraph-report-tabs` | Create, duplicate, rename, and reorder report tabs. |
| `whatagraph-widgets` | Build and lay out widgets on the grid. |
| `whatagraph-dynamic-charts` | Build chart families with no dedicated widget type — scatter, bubble, heatmap, calendar heatmap, candlestick, box plot, radar, funnel, polar bar, stacked and 100% stacked, horizontal bars, bars-plus-line, top-N. |
| `whatagraph-offline-reports` | Build a whole report from numbers you already have, with no connected source. |
| `whatagraph-blends` | Combine data from different channels into one virtual source. |
| `whatagraph-source-groups` | Roll up multiple accounts — same-channel or cross-channel — into one aggregated source. |
| `whatagraph-custom-metrics` | Create calculated or unified metrics across sources. |
| `whatagraph-custom-dimensions` | Create derived dimensions — tag-based, condition-based, or AI-classified groupings. |
| `whatagraph-filters` | Create reusable saved filter configurations for a channel. |
| `whatagraph-overviews` | Create overviews — KPI dashboards (called "Measurements" in the UI). |
| `whatagraph-goals` | Create goals — metric targets with a deadline. |
| `whatagraph-templates` | Convert a report into a reusable template and apply templates to new reports. |
| `whatagraph-themes` | Apply and manage themes (logos, fonts, headers/footers) and color palettes. |
| `whatagraph-assets` | Import, find, read and publish files — brand images for reports and themes, and searchable documents. |
| `whatagraph-sharing` | Create and update public share links for reports. |
| `whatagraph-automations` | Schedule automated report delivery by email. |
| `whatagraph-snapshots` | Save and restore the structural state of a report. |
| `whatagraph-integrations-admin` | Connect sources from already-authenticated accounts and assign them to spaces. |
| `whatagraph-dynamic-integrations` | Build a data source Whatagraph does not support yet, from the API's own documentation, with no code deploy. |
| `whatagraph-team-and-members` | View team settings and subscription; invite and update team members. |
| `whatagraph-customer-patterns` | Common multi-tool flows and decision trees across skills. |
| `whatagraph-deleting` | Safe deletion, removal, and revocation across Whatagraph entities. |

### Team computer and browser (IQ agents)

These three skills are written for Whatagraph's own IQ agents, which load them from this
repository when they work on the team computer and in the agent's browser. They describe tools
that exist only inside the Whatagraph app (`computer-exec`, `browser-navigate` and the others), so
they do nothing for a Claude client that uses the MCP server alone.

| Skill | What it does |
|---|---|
| `team-computer` | Python analysis, files, charts and downloadable deliverables on the team computer. Long commands run as background jobs and the conversation wakes on completion. Data from an outside API is requested through the platform, with a secret from the person's vault. Every deck and workbook is checked before it is handed over. |
| `team-browser` | Read and act on approved websites in the browser that belongs to the acting person: site and action approvals, pictures of pages for a deck, and sign-ins from the person's saved sign-in or the one they typed in the conversation, which the agent never sees in clear text. |
| `board-pack` | Prepare a long pack (a board pack, a quarterly review, a competitor study with thirty or more slides) alone from one request: stages over several turns, state kept in files, research read from pages the browser opened, and the checks before delivery. |

## Skill frontmatter — declaring tools

Each `SKILL.md` declares the MCP tools it uses in YAML frontmatter, split into
two lists:

- **`required_tools`** — the **core** tools the skill's main happy path invokes.
  A skill is only offered to an agent that has all of its `required_tools`.
- **`optional_tools`** — tools used only in optional sub-workflows, verification
  steps, or decision-table alternatives. Absent = an empty list (identical to
  declaring none). Each entry is either a bare tool name or a
  `{tool_name, purpose}` mapping; `purpose` is surfaced downstream when present.

  ```yaml
  optional_tools:
    - tool_name: export-report
      purpose: Verify the built widgets render with data.
    - list-filters
  ```

**Authoring rule:** every tool the skill body actually invokes must appear in
`required_tools` **or** `optional_tools`; alternatives and branch-only tools go
in `optional_tools`, never in core; and no tool may appear in both lists. These
rules are enforced in CI by `scripts/lint_skill_tools.py` (run it locally with
`python3 scripts/lint_skill_tools.py`).

## License

Apache License 2.0. See [LICENSE](LICENSE) for details.
