# Whatagraph Agent Skills

Source repository for the [Agent Skills](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview) served by the Whatagraph MCP server.

## Overview

Whatagraph is a marketing data platform that connects 60+ marketing channels (Google Ads, GA4, Shopify, Salesforce, Mailchimp, and more) into unified reports, dashboards, and automated deliveries. The Whatagraph MCP server exposes the platform so an agent can browse connected data sources, fetch data, and — where enabled — build and maintain reports, source groups, blends, custom metrics and dimensions, measurements, goals, sharing, automations, and more.

The skills in this repo are loaded directly by the MCP server. Agents discover and load them on demand through the server's `list-skills` and `load-skill` tools — there is no separate install step.

## Connecting the MCP server

- Server info: [https://mcp.whatagraph.com](https://mcp.whatagraph.com)
- MCP endpoint: `https://mcp.whatagraph.com/mcp`

Add the server endpoint to your MCP client using your Whatagraph account's normal MCP setup flow. Once connected, the agent will pick up the relevant skills automatically when it works on a Whatagraph task.

## Availability

Skill-assisted workflows are being rolled out gradually. If skills aren't showing up for your account yet, reach out to Whatagraph support.

Read tools (browsing data, fetching metrics, exporting reports) are available on all plans. Write and delete tools (creating, updating, or deleting reports, widgets, source groups, blends, custom metrics and dimensions, goals, sharing, automations, etc.) may require enablement for your team.

## Contributing

Issues and pull requests are welcome.

## License

Apache License 2.0. See [LICENSE](LICENSE) for details.
