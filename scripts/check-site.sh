#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

if [ "$#" -gt 0 ]; then
  echo "Usage: bash scripts/check-site.sh"
  echo "Build once in a temporary directory, check operational-file exclusions, and clean up."
  case "$1" in -h|--help) exit 0 ;; *) exit 2 ;; esac
fi

CHECK_DIR="$(mktemp -d "${TMPDIR:-/tmp}/blog-site-check.XXXXXX")"
trap 'rm -rf -- "$CHECK_DIR"' EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

# Jekyll 3 does not expose --disable-disk-cache; configuration also works with v4.
cat > "$CHECK_DIR/validation.yml" <<'EOF'
incremental: false
disable_disk_cache: true
sass:
  cache: false
EOF

cd "$PROJECT_ROOT"
JEKYLL_ENV=production bash "$SCRIPT_DIR/jekyll.sh" build \
  --strict_front_matter \
  --config "$PROJECT_ROOT/_config.yml,$CHECK_DIR/validation.yml" \
  --destination "$CHECK_DIR/site"

for excluded in AGENTS.md README.md SEO.md WORKFLOW.md SKILL.md skill.md scripts docs .agents .codex .github vendor Gemfile Gemfile.lock; do
  rendered="$excluded"
  case "$excluded" in *.md) rendered="${excluded%.md}.html" ;; esac
  if [ -e "$CHECK_DIR/site/$excluded" ] || [ -e "$CHECK_DIR/site/$rendered" ]; then
    echo "Operational file or directory leaked into the site: $excluded" >&2
    exit 1
  fi
done

test -s "$CHECK_DIR/site/index.html"
echo "Site validation passed: production build, home output, operational-file exclusions."
