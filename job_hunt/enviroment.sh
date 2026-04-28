#!/usr/bin/env bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export DAIANA_JOB_HUNT_DIR="$SCRIPT_DIR"

ENV_FILE="$DAIANA_JOB_HUNT_DIR/.env"
PROMPTS_DIR="$DAIANA_JOB_HUNT_DIR/prompts"

if [ ! -d "$PROMPTS_DIR" ]; then
  echo "Error: prompts directory not found at:"
  echo "  $PROMPTS_DIR"
  return 1 2>/dev/null || exit 1
fi

if [ ! -f "$ENV_FILE" ]; then
  echo "Error: .env file not found at:"
  echo "  $ENV_FILE"
  return 1 2>/dev/null || exit 1
fi

set -a
source "$ENV_FILE"
set +a

echo ""
echo "Loaded DAIANA_JOB_HUNT_DIR:"
echo "  $DAIANA_JOB_HUNT_DIR"
echo "Loaded prompts directory:"
echo "  $PROMPTS_DIR"

if [ -n "${PERPLEXITY_API_KEY:-}" ]; then
  echo "PERPLEXITY_API_KEY loaded"
else
  echo "Warning: PERPLEXITY_API_KEY is missing"
fi

if [ -n "${OPENAI_API_KEY:-}" ]; then
  echo "OPENAI_API_KEY loaded"
else
  echo "Warning: OPENAI_API_KEY is missing"
fi
echo ""