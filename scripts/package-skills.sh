#!/usr/bin/env bash
# Package each skill in skills/ into its own .zip under dist/, for upload
# to Claude.ai's web interface (which accepts one zip per skill).
#
# Usage:
#   ./scripts/package-skills.sh            # packages every skill
#   ./scripts/package-skills.sh NAME [...] # packages only the named skills
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
skills_dir="$repo_root/skills"
dist_dir="$repo_root/dist"

if [ ! -d "$skills_dir" ]; then
  echo "error: $skills_dir not found" >&2
  exit 1
fi

mkdir -p "$dist_dir"

if [ "$#" -gt 0 ]; then
  targets=("$@")
else
  targets=()
  while IFS= read -r -d '' dir; do
    targets+=("$(basename "$dir")")
  done < <(find "$skills_dir" -mindepth 1 -maxdepth 1 -type d -print0)
fi

for name in "${targets[@]}"; do
  src="$skills_dir/$name"
  if [ ! -d "$src" ]; then
    echo "skip: $name (not found at $src)" >&2
    continue
  fi
  out="$dist_dir/$name.zip"
  rm -f "$out"
  (cd "$skills_dir" && zip -q -r "$out" "$name")
  echo "packaged: $out"
done
