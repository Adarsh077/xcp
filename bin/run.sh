#!/usr/bin/env bash
set -euo pipefail

IMAGE="xcp"
PORT=8000

docker build -t "$IMAGE" "$(dirname "$0")/.."
docker run --rm -p "$PORT:$PORT" --env-file "$(dirname "$0")/../.env" "$IMAGE"
