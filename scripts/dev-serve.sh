#!/usr/bin/env bash
set -euo pipefail

if ! command -v ruby >/dev/null 2>&1; then
  echo "ruby is not installed."
  echo "Ubuntu example:"
  echo "  sudo apt update"
  echo "  sudo apt install -y ruby-full build-essential zlib1g-dev libffi-dev libyaml-dev"
  exit 1
fi

PORT="${PORT:-8666}"
HOST="${HOST:-127.0.0.1}"
USER_GEM_BIN="$(ruby -e 'require "rubygems"; print Gem.bindir(Gem.user_dir)')"
export BUNDLE_PATH="${BUNDLE_PATH:-$PWD/vendor/bundle}"
export BUNDLE_CACHE_PATH="${BUNDLE_CACHE_PATH:-$PWD/vendor/cache}"
export BUNDLE_APP_CONFIG="${BUNDLE_APP_CONFIG:-$PWD/.bundle}"
export BUNDLE_DISABLE_SHARED_GEMS="true"

if [ -d "$USER_GEM_BIN" ]; then
  export PATH="$USER_GEM_BIN:$PATH"
fi

if ! command -v bundle >/dev/null 2>&1; then
  echo "bundler is not installed in a runnable path."
  echo "Installing bundler to your user gem directory..."
  gem install --user-install bundler
  export PATH="$USER_GEM_BIN:$PATH"
fi

bundle config set --local path "$BUNDLE_PATH"
bundle config set --local cache_path "$BUNDLE_CACHE_PATH"
bundle config set --local app_config "$BUNDLE_APP_CONFIG"
bundle config set --local disable_shared_gems true
bundle install

exec bundle exec jekyll serve \
  --host "$HOST" \
  --port "$PORT"
