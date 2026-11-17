---
name: whatagraph-team-and-members
type: domain
group: team_workspace_branding
description: View team settings and subscription, update team name/localization, invite or update team members, and read or manage roles (pre-made and custom, account-wide or per space) for members and agents. Use when a user wants to onboard a new team member, change roles, create a custom role, give someone a role in one space, update team timezone/currency defaults, or inspect plan limits.
required_tools:
  - list-automations
  - view-team
  - manage-members
  - manage-sources
  - manage-team
optional_tools:
  - tool_name: remove-members
    purpose: Cancel a pending member invitation.
  - tool_name: list-roles
    purpose: Read roles, their abilities, and who holds which role where.
  - tool_name: manage-roles
    purpose: Create or change custom roles, and assign or revoke roles for members and agents.
  - tool_name: delete-roles
    purpose: Delete a custom role.
---

# Team & members

Tools covered: `view-team`, `manage-team`, `manage-members`, `remove-members`, `list-roles`, `manage-roles`, `delete-roles`.

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

- `role` — discover the roles you may give via `view-team action=roles`. Always: `admin` (only an admin can give it), `manager`, `editor`. Teams with custom roles also get `space_manager`, `viewer` and `client_viewer`.
- `spaces` — required for every space-scoped role (`editor`, `space_manager`, `viewer`, `client_viewer`); restricts the member to the listed spaces.
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

Get `member_id` from `view-team action=members`. For space-scoped roles, you must pass the complete `spaces` list — it **replaces** current access, so omitting a space removes it. Admin/manager roles ignore `spaces` and are reset to all-space access on each role change.

## Roles and what they allow

A role is a set of abilities named `domain.action`, such as `reports.view` or `sharing.manage`. Read them before you promise what someone can do:

```
list-roles action=list          # pre-made and custom roles, each with its abilities
list-roles action=abilities     # every ability a role can hold
list-roles action=principals    # members and agents with the roles they hold, account-wide or per space
```

Pre-made roles:

| Role | For | Scope |
|---|---|---|
| Admin | everything, including billing and roles | whole account |
| Manager | everything except billing, building integrations and changing roles | whole account |
| Editor | build and share reports, connect sources | assigned spaces |
| Space Manager | an editor who also manages the space's members | assigned spaces |
| Viewer | read reports | assigned spaces |
| Client Viewer | read reports, without the list of spaces | assigned spaces |
| Agent Operator | for agents: build and change reports | assigned spaces |
| Agent Viewer | for agents: read reports | assigned spaces |

Space Manager, Viewer, Client Viewer and custom roles are available only to teams that have custom roles.

## Custom roles and roles per space

```
manage-roles action=create title="Analyst" abilities=["reports.view","widgets.view","sharing.view"]
manage-roles action=update role_id=<id> abilities=[...]
manage-roles action=assign role_id=<id> principal_type=member principal_id=<member_id> space_id=<space_id>
manage-roles action=revoke role_id=<id> principal_type=agent principal_id=<agent_id>
delete-roles role_id=<id>
```

- Leave `space_id` empty to give the role on the whole account. With `space_id`, the role applies only in that space, so one person can be an Editor in one space and a Viewer in another.
- Pre-made roles cannot be changed or deleted. Deleting a custom role takes it from everyone who held it.
- Nobody can create or give a role with an ability they do not hold themselves. A refusal for that reason is final: tell the user which ability is missing instead of retrying.
- An agent's role limits the agent, and an agent never does more than the person it acts for may do. If a tool call is refused for permissions, say so plainly; do not look for another tool to do the same thing.

## Cancelling a pending invitation

```
remove-members action=cancel_invite invite_id=<id>
```

Only cancels **pending** invites — accepted members cannot be removed via MCP (UI only). Use `view-team action=invites` to find invite IDs.

## What MCP can't do here

- Remove an accepted member — UI only (`remove-members` only cancels pending invites).
- List pending invites — no read action exists; `invite_id` comes from the invite response.
- View audit log of member actions — UI only.

## Common pitfalls

- **A space-scoped role without `spaces`** — rejected; `editor`, `space_manager`, `viewer` and `client_viewer` must list allowed spaces.
- **Invite same email twice** — second invite either no-ops or replaces the first; use `resend_invite` if the user didn't get the email.
- **Role name casing** — use the lowercase names (`admin`, `manager`, `editor`, …) as returned by `action=roles`.
- **Admin role is powerful** — grants full platform access. Prefer `editor` or `viewer` + specific spaces for everyday users.
- **Changing team timezone retroactively** — existing automations keep their schedule in the old timezone. Review `list-automations` after timezone changes.
- **Seat limits** — `view-team action=show_subscription` returns used/available seats. Invites may fail when the team is over the limit.
