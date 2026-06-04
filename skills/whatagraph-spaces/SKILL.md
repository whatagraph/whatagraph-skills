---
name: whatagraph-spaces
description: Create and manage spaces (also called client folders). Spaces are the top-level containers for reports and data sources. Use when onboarding a new client, organizing reports into folders, or nesting folders for multi-brand/agency hierarchies.
required_tools:
  - manage-spaces
  - delete-spaces
---

# Spaces (client folders)

Tools covered: `list-spaces`, `manage-spaces`, `delete-spaces`.

A **space** is a top-level container that organizes reports and data sources. In the UI it's labeled as a space or folder. Every team has a "Home" space by default (not editable).

## Use this when

- "Create a new client folder for Acme Corp."
- "Nest sub-spaces for each brand under this parent."
- "Show me all spaces for this team."

## Listing

```
list-spaces action=list                                  # paginated; top-level only
list-spaces action=list include_home=true                # include home
list-spaces action=show client_id=<id>                   # report/measurement counts
list-spaces action=children client_id=<id>               # sub-spaces
```

## Create a space

```
manage-spaces action=create
   name="Acme Corp"
   description="Acme's reports and data sources"
```

## Create a sub-space (nested)

```
manage-spaces action=create
   name="Acme — Paid Media"
   parent_id=<parent_space_id>
```

## Update

```
manage-spaces action=update client_id=<id>
   name="..." description="..."
```

Cannot update the Home space.

## Deleting a space

```
delete-spaces action=delete client_id=<id>
```

The parameter is `client_id` (same as on create/update). Reports and measurements inside the space are soft-deleted with it; support can restore within the retention window. Cannot delete the Home space. Always confirm with the user — deleting a client folder is visible to the whole team.

## What MCP can't do here

- Move a space to a different parent after creation — UI only (where supported).
- Assign users/permissions to a space — via `manage-members` for editor role.

## Common pitfalls

- **`space_id` vs `client_id`** — MCP uses `client_id`. The UI says "space/folder"; the code says `team_client`. All point at the same thing.
- **Nesting too deep** — 1–2 levels is manageable; 4+ creates a clicky navigation.
- **Assuming a space owns sources** — sources are assigned to spaces via `manage-integrations action=sync_to_clients`, not at source creation.
- **Deleting in UI breaks reports** — reports that live in the space are soft-deleted with it; they can be restored via support but not MCP.
