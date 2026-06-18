---
name: whatagraph-team-and-members
description: View team settings and subscription, update team name/localization, and invite or update team member invitations. Use when a user wants to onboard a new team member, change roles, update team timezone/currency defaults, or inspect plan limits.
required_tools:
  - list-automations
  - view-team
  - manage-members
  - manage-sources
  - manage-team
---

# Team & members

Tools covered: `view-team`, `manage-team`, `manage-members`.

## View team info and subscription

```
view-team action=show                    # team name, enabled features
view-team action=show_subscription       # plan + usage limits
view-team action=list_plans              # all available plans
view-team action=roles                   # available roles
view-team action=search search="acme"    # global cross-domain search
```

Use `view-team action=search` when you don't know which domain (reports, overviews, spaces) contains the match.

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

## Cancelling a pending invitation

Destructive — covered in the `whatagraph-deleting` skill (load it for parameters, cascades, and recovery). Quick facts: `remove-members` only cancels *pending* invites, `invite_id` comes from `manage-members`, accepted members can only be removed in the UI.

## What MCP can't do here

- Remove an accepted member — UI only.
- Change role on an accepted member — UI only.
- Set custom permissions beyond admin/manager/editor — UI only (Enterprise plans).
- View audit log of member actions — UI only.

## Common pitfalls

- **`editor` role without `spaces`** — rejected; editors are space-scoped and must list allowed spaces.
- **Invite same email twice** — second invite either no-ops or replaces the first; use `resend_invite` if the user didn't get the email.
- **Role name casing** — use lowercase (`admin`, `manager`, `editor`) as returned by `action=roles`.
- **Admin role is powerful** — grants full platform access. Prefer `editor` + specific spaces for everyday users.
- **Changing team timezone retroactively** — existing automations keep their schedule in the old timezone. Review `list-automations` after timezone changes.
- **Seat limits** — `view-team action=show_subscription` returns used/available seats. Invites may fail when the team is over the limit.
