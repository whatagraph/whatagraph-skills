#!/usr/bin/env bash
#
# Install or update the Whatagraph MCP skills under ~/.claude/skills/.
#
# Usage:
#   ./install.sh                # install to ~/.claude/skills
#   ./install.sh /custom/path   # install to a custom skills directory
#
# Behavior:
#   - Backs up any existing whatagraph-* skills under <target>/.whatagraph-backup-<timestamp>/
#   - Copies every whatagraph-* skill directory from this plugin's skills/ folder into <target>/
#   - Prints a summary of what was installed, updated, or skipped.
#
# Idempotent: safe to re-run. Re-running picks up any local edits in the plugin's skills/.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC_SKILLS="$SCRIPT_DIR/skills"

if [[ ! -d "$SRC_SKILLS" ]]; then
  echo "❌ Could not find skills/ next to install.sh (looked at: $SRC_SKILLS)" >&2
  exit 1
fi

TARGET="${1:-$HOME/.claude/skills}"
mkdir -p "$TARGET"

# Find existing whatagraph-* skills to back up.
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
BACKUP_DIR="$TARGET/.whatagraph-backup-$TIMESTAMP"
EXISTING_COUNT=0

while IFS= read -r -d '' existing; do
  if [[ -d "$existing" ]]; then
    if [[ "$EXISTING_COUNT" -eq 0 ]]; then
      mkdir -p "$BACKUP_DIR"
    fi
    mv "$existing" "$BACKUP_DIR/"
    EXISTING_COUNT=$((EXISTING_COUNT + 1))
  fi
done < <(find "$TARGET" -maxdepth 1 -type d -name 'whatagraph-*' -print0)

if [[ "$EXISTING_COUNT" -gt 0 ]]; then
  echo "📦 Backed up $EXISTING_COUNT existing whatagraph-* skill(s) to:"
  echo "   $BACKUP_DIR"
fi

# Copy each skill directory into the target.
INSTALLED=0
for src in "$SRC_SKILLS"/whatagraph-*/; do
  name=$(basename "$src")
  cp -R "$src" "$TARGET/$name"
  INSTALLED=$((INSTALLED + 1))
done

echo "✅ Installed $INSTALLED Whatagraph MCP skill(s) to:"
echo "   $TARGET"
echo
echo "   Skills installed:"
ls "$TARGET" | grep '^whatagraph-' | sed 's/^/     - /'

if [[ "$EXISTING_COUNT" -gt 0 ]]; then
  echo
  echo "ℹ️  If everything works, you can delete the backup:"
  echo "    rm -rf '$BACKUP_DIR'"
fi
