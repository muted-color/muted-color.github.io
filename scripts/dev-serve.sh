#!/usr/bin/env bash
set -euo pipefail

MIN_RUBY_VERSION="3.2.0"

version_ge() {
  [ "$(printf '%s\n%s\n' "$1" "$2" | sort -V | head -n 1)" = "$2" ]
}

ensure_supported_ruby() {
  local current_version=""
  local -a ruby_bin_candidates=(
    "/opt/homebrew/opt/ruby@3.2/bin"
    "/opt/homebrew/opt/ruby@3.3/bin"
    "/opt/homebrew/opt/ruby@3.4/bin"
    "/opt/homebrew/opt/ruby/bin"
    "/usr/local/opt/ruby@3.2/bin"
    "/usr/local/opt/ruby@3.3/bin"
    "/usr/local/opt/ruby@3.4/bin"
    "/usr/local/opt/ruby/bin"
  )

  if command -v ruby >/dev/null 2>&1; then
    current_version="$(ruby -e 'print RUBY_VERSION')"
    if version_ge "$current_version" "$MIN_RUBY_VERSION"; then
      return 0
    fi
  fi

  for ruby_bin_dir in "${ruby_bin_candidates[@]}"; do
    if [ ! -x "$ruby_bin_dir/ruby" ]; then
      continue
    fi

    current_version="$("$ruby_bin_dir/ruby" -e 'print RUBY_VERSION')"
    if version_ge "$current_version" "$MIN_RUBY_VERSION"; then
      export PATH="$ruby_bin_dir:$PATH"
      return 0
    fi
  done

  echo "ruby ${MIN_RUBY_VERSION}+ is required."
  if [ -n "$current_version" ] && command -v ruby >/dev/null 2>&1; then
    echo "Current ruby: $current_version ($(command -v ruby))"
  fi
  echo "macOS with Homebrew example:"
  echo "  brew install ruby@3.2"
  echo "  export PATH=\"/opt/homebrew/opt/ruby@3.2/bin:\$PATH\""
  exit 1
}

if ! command -v ruby >/dev/null 2>&1; then
  echo "ruby is not installed."
  echo "Ubuntu example:"
  echo "  sudo apt update"
  echo "  sudo apt install -y ruby-full build-essential zlib1g-dev libffi-dev libyaml-dev"
  exit 1
fi

ensure_supported_ruby

PORT="${PORT:-8666}"
HOST="${HOST:-127.0.0.1}"
USER_GEM_BIN="$(ruby -e 'require "rubygems"; print Gem.bindir(Gem.user_dir)')"
LOCKFILE_BUNDLER_VERSION="$(
  ruby -e '
    lockfile = File.join(Dir.pwd, "Gemfile.lock")
    unless File.exist?(lockfile)
      exit
    end

    lines = File.readlines(lockfile, chomp: true)
    index = lines.rindex("BUNDLED WITH")
    if index && lines[index + 1]
      puts lines[index + 1].strip
    end
  '
)"
BUNDLER_VERSION="${BUNDLER_VERSION:-${LOCKFILE_BUNDLER_VERSION:-2.4.22}}"
export BUNDLE_PATH="${BUNDLE_PATH:-$PWD/vendor/bundle}"
export BUNDLE_CACHE_PATH="${BUNDLE_CACHE_PATH:-$PWD/vendor/cache}"
export BUNDLE_APP_CONFIG="${BUNDLE_APP_CONFIG:-$PWD/.bundle}"
export BUNDLE_DISABLE_SHARED_GEMS="true"

if [ -d "$USER_GEM_BIN" ]; then
  export PATH="$USER_GEM_BIN:$PATH"
fi

if ! gem list -i bundler -v "$BUNDLER_VERSION" >/dev/null 2>&1; then
  echo "bundler $BUNDLER_VERSION is not installed."
  echo "Installing bundler $BUNDLER_VERSION to your user gem directory..."
  if ! gem install --user-install bundler -v "$BUNDLER_VERSION"; then
    echo "Failed to install bundler $BUNDLER_VERSION."
    echo "ruby $(ruby -e 'print RUBY_VERSION') is not compatible with this bundle."
    exit 1
  fi
  export PATH="$USER_GEM_BIN:$PATH"
fi

BUNDLE_CMD=(bundle "_${BUNDLER_VERSION}_")

"${BUNDLE_CMD[@]}" config set --local path "$BUNDLE_PATH"
"${BUNDLE_CMD[@]}" config set --local cache_path "$BUNDLE_CACHE_PATH"
"${BUNDLE_CMD[@]}" config set --local app_config "$BUNDLE_APP_CONFIG"
"${BUNDLE_CMD[@]}" config set --local disable_shared_gems true
"${BUNDLE_CMD[@]}" install

exec "${BUNDLE_CMD[@]}" exec jekyll serve \
  --host "$HOST" \
  --port "$PORT"
