---
name: whatagraph-team-and-members
type: domain
group: team_workspace_branding
description: View team settings and subscription, update team name/localization, and invite or update team member invitations. Use when a user wants to onboard a new team member, change roles, update team timezone/currency defaults, or inspect plan limits.
required_tools:
  - list-automations
  - view-team
  - manage-members
  - manage-sources
  - manage-team
optional_tools:
  - tool_name: remove-members
    purpose: Cancel a pending member invitation.
---

# Team & members

Tools covered: `view-team`, `manage-team`, `manage-members`, `remove-members`.

## View team info and subscription

```
view-team action=show                    # team name, enabled features
view-team action=show_subscription       # plan + usage limits
view-team action=members                 # seated members with member_id, name, email, role
view-team action=list_plans              # all available plans
view-team action=roles                   # available roles
view-team action=search search="acme"    # global cross-domain search
```

Use `view-team action=members` to get `member_id` values needed for `update_member_role`. Use `view-team action=search` when you don't know which domain (reports, overviews, spaces) contains the match.

## Update team settings

```
manage-team action=update
   name="Acme Agency"
   settings={
     "timezone": "Europe/London",
     "currency": "GBP",
     "decimal_place": 2,
     "start_of_week": 1,
     "region": "EU",
     "text_direction": "ltr"
   }
```

Team settings apply platform-wide defaults. Individual sources can override currency via `manage-sources action=set_currency`.

## Invite a new team member

```
manage-members action=invite
   email="<member_email>"
   role="editor"
   spaces=[{"id": <space_id_1>}, {"id": <space_id_2>}]
```

- `role` — discover available roles via `view-team action=roles`. Values: `admin`, `manager`, `editor`.
- `spaces` — required for `editor` role; restricts the editor to listed spaces.
- Omit `spaces` for `admin` and `manager`.

## List pending invitations

```
view-team action=invites
```

Returns all pending invitations with `invite_id`, email, role, spaces (for editors), and `created_at`. Use the `invite_id` from this list with `manage-members` for `update_invite`, `resend_invite`, or `remove-members` for `cancel_invite`.

## Update a pending invitation

```
manage-members action=update_invite
   invite_id=<id>
   role="manager"
```

Changes role on a pending (not-yet-accepted) invitation.

## Resend an invitation

```
manage-members action=resend_invite invite_id=<id>
```

## Change role on an accepted member

```
manage-members action=update_member_role
   member_id=<id>                          # from view-team action=members
   role="editor"
   spaces=[{"id": <space_id>}]            # required for editor role
```

Get `member_id` from `view-team action=members`. For editors, you must pass the complete `spaces` list — it **replaces** current access, so omitting a space removes it. Admin/manager roles ignore `spaces` and are reset to all-space access on each role change.

## Cancelling a pending invitation

```
remove-members action=cancel_invite invite_id=<id>
```

Only cancels **pending** invites — accepted members cannot be removed via MCP (UI only). Use `view-team action=invites` to find invite IDs.

## What MCP can't do here

- Remove an accepted member — UI only (`remove-members` only cancels pending invites).
- List pending invites — no read action exists; `invite_id` comes from the invite response.
- Set custom permissions beyond admin/manager/editor — UI only (Enterprise plans).
- View audit log of member actions — UI only.

## Common pitfalls

- **`editor` role without `spaces`** — rejected; editors are space-scoped and must list allowed spaces.
- **Invite same email twice** — second invite either no-ops or replaces the first; use `resend_invite` if the user didn't get the email.
- **Role name casing** — use lowercase (`admin`, `manager`, `editor`) as returned by `action=roles`.
- **Admin role is powerful** — grants full platform access. Prefer `editor` + specific spaces for everyday users.
- **Changing team timezone retroactively** — existing automations keep their schedule in the old timezone. Review `list-automations` after timezone changes.
- **Seat limits** — `view-team action=show_subscription` returns used/available seats. Invites may fail when the team is over the limit.
