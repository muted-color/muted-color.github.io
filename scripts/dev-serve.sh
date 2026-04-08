#!/usr/bin/env bash
set -euo pipefail

PORT="${PORT:-8666}"
HOST="${HOST:-127.0.0.1}"

if ! command -v ruby >/dev/null 2>&1; then
  echo "ruby is not installed."
  echo "Ubuntu example:"
  echo "  sudo apt update"
  echo "  sudo apt install -y ruby-full build-essential zlib1g-dev libffi-dev libyaml-dev"
  exit 1
fi

if ! command -v bundle >/dev/null 2>&1; then
  echo "bundler is not installed."
  echo "Install it with:"
  echo "  gem install bundler"
  exit 1
fi

bundle install

exec bundle exec jekyll serve \
  --livereload \
  --host "$HOST" \
  --port "$PORT"
