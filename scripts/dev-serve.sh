#!/usr/bin/env bash
set -euo pipefail

# Keep the existing service entrypoint; dependency installation is explicit setup.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec bash "$SCRIPT_DIR/jekyll.sh" serve "$@"
