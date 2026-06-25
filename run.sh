#!/usr/bin/env bash
# CORE root shortcut - forwards to scripts/run.sh

set -e

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "$ROOT_DIR/scripts/run.sh" "$@"
