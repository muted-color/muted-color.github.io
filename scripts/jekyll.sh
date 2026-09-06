#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
MIN_RUBY_VERSION="3.2.0"

usage() {
  cat <<'EOF'
Usage: bash scripts/jekyll.sh <setup|check|exec|build|serve> [arguments...]

  setup  Install the locked Bundler and dependencies (explicit network/setup step).
  check  Check installed dependencies without installing or changing the lockfile.
  exec   Run a command inside the installed bundle.
  build  Run Jekyll build; use scripts/check-site.sh for an isolated validation build.
  serve  Run Jekyll serve (HOST=127.0.0.1, PORT=8666 by default).

Routine commands never install gems or rewrite Bundler configuration.
EOF
}

MODE="${1:-}"
case "$MODE" in
  -h|--help|help) usage; exit 0 ;;
  setup|check|exec|build|serve) shift ;;
  *) usage >&2; exit 2 ;;
esac
if { [ "$MODE" = "setup" ] || [ "$MODE" = "check" ]; } && [ "$#" -ne 0 ]; then
  usage >&2
  exit 2
fi
if [ "$MODE" = "exec" ] && [ "$#" -eq 0 ]; then
  usage >&2
  exit 2
fi

select_ruby() {
  local candidate
  local -a candidates=()
  if command -v ruby >/dev/null 2>&1; then
    candidates+=("$(command -v ruby)")
  fi
  if [ -n "${CONDA_PREFIX:-}" ]; then
    candidates+=("$CONDA_PREFIX/bin/ruby")
  fi
  candidates+=(
    "$HOME/miniforge3/bin/ruby"
    "$HOME/miniconda3/bin/ruby"
    "/opt/homebrew/opt/ruby@3.2/bin/ruby"
    "/opt/homebrew/opt/ruby@3.3/bin/ruby"
    "/opt/homebrew/opt/ruby@3.4/bin/ruby"
    "/opt/homebrew/opt/ruby/bin/ruby"
    "/usr/local/opt/ruby@3.2/bin/ruby"
    "/usr/local/opt/ruby@3.3/bin/ruby"
    "/usr/local/opt/ruby@3.4/bin/ruby"
    "/usr/local/opt/ruby/bin/ruby"
  )
  for candidate in "${candidates[@]}"; do
    if [ -x "$candidate" ] && "$candidate" -rrubygems -e \
      'exit(Gem::Version.new(RUBY_VERSION) >= Gem::Version.new(ARGV.fetch(0)) ? 0 : 1)' \
      "$MIN_RUBY_VERSION"; then
      export PATH="$(dirname "$candidate"):$PATH"
      return 0
    fi
  done
  echo "Ruby ${MIN_RUBY_VERSION}+ is required; install Ruby and add its bin directory to PATH." >&2
  return 1
}

cd "$PROJECT_ROOT"
select_ruby

BUNDLER_VERSION="$(ruby -e '
  lock = File.read("Gemfile.lock")
  version = lock[/^BUNDLED WITH\s*\n\s*(\S+)/, 1]
  abort "Gemfile.lock must specify BUNDLED WITH" unless version
  print version
')"
USER_GEM_BIN="$(ruby -rrubygems -e 'print Gem.bindir(Gem.user_dir)')"
export PATH="$USER_GEM_BIN:$PATH"
export BUNDLE_GEMFILE="$PROJECT_ROOT/Gemfile"
export BUNDLE_PATH="$PROJECT_ROOT/vendor/bundle"
export BUNDLE_CACHE_PATH="$PROJECT_ROOT/vendor/cache"
export BUNDLE_APP_CONFIG="$PROJECT_ROOT/.bundle"
export BUNDLE_DISABLE_SHARED_GEMS="true"
export BUNDLE_FROZEN="true"

if ! ruby -rrubygems -e 'exit(Gem::Specification.find_all_by_name("bundler", ARGV.fetch(0)).empty? ? 1 : 0)' "$BUNDLER_VERSION"; then
  if [ "$MODE" != "setup" ]; then
    echo "Bundler $BUNDLER_VERSION is missing. Run: bash scripts/jekyll.sh setup" >&2
    exit 1
  fi
  ruby -S gem install --user-install bundler -v "$BUNDLER_VERSION" --no-document
fi

BUNDLE_CMD=(ruby -S bundle "_${BUNDLER_VERSION}_")

case "$MODE" in
  setup) exec "${BUNDLE_CMD[@]}" install ;;
  check) exec "${BUNDLE_CMD[@]}" check ;;
esac

if ! "${BUNDLE_CMD[@]}" check; then
  echo "Dependencies are not ready. Run: bash scripts/jekyll.sh setup" >&2
  echo "For a new architecture, add its platform to Gemfile.lock as a separate dependency change." >&2
  exit 1
fi

case "$MODE" in
  exec) exec "${BUNDLE_CMD[@]}" exec "$@" ;;
  build) exec "${BUNDLE_CMD[@]}" exec jekyll build "$@" ;;
  serve)
    exec "${BUNDLE_CMD[@]}" exec jekyll serve \
      --host "${HOST:-127.0.0.1}" --port "${PORT:-8666}" "$@"
    ;;
esac
