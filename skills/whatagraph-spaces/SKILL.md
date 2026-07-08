---
name: whatagraph-spaces
type: domain
description: Create and manage spaces (also called client folders). Spaces are the top-level containers for reports and data sources. Use when onboarding a new client, organizing reports into folders, or nesting folders for multi-brand/agency hierarchies. Handles asks like "create a folder for a new client", "organize my reports into folders", or "set up a sub-folder under this client".
required_tools:
  - list-spaces
  - manage-integrations
  - manage-members
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
list-spaces action=list search="Acme"                    # filter by name
list-spaces action=list sort_by="name-asc"               # newest (default), oldest, name-asc, name-desc
list-spaces action=show client_id=<id>                   # report/measurement counts
list-spaces action=children client_id=<id>               # sub-spaces (each child includes its parent_id)
```

Pagination: cursor-based with `cursor` parameter; `per_page` up to 500 (default 100).

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

Update accepts any combination of `name`, `description`, and `parent_id` — at least one is required.

### Move a space to a different parent

```
manage-spaces action=update client_id=<id>
   parent_id=<new_parent_id>          # move under another space
```

Pass `parent_id=0` to move a space to the root level (no parent).
Self-parenting and circular hierarchies are rejected automatically.

Cannot update the Home space.

## Deleting a space

```
delete-spaces action=delete client_id=<id>
```

Soft-deletes the space and all its reports/measurements (support-restorable within retention window). The Home space cannot be deleted. The parameter is `client_id`, not `space_id`. See `whatagraph-deleting` for full context.

## What MCP can't do here

- Bulk-move multiple spaces at once — move them one at a time with `manage-spaces action=update parent_id=<id>`.
- Assign users/permissions to a space — via `manage-members` for editor role.

## Common pitfalls

- **`space_id` vs `client_id`** — MCP uses `client_id`. The UI says "space/folder"; the code says `team_client`. All point at the same thing.
- **Nesting too deep** — 1–2 levels is manageable; 4+ creates a clicky navigation.
- **Assuming a space owns sources** — sources are assigned to spaces via `manage-integrations action=sync_to_clients`, not at source creation.
- **Deleting a space cascades to its reports** — reports that live in the space are soft-deleted with it; they can be restored via support but not MCP.
