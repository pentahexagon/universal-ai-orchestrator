#!/usr/bin/env bash
# Use gh CLI to set repository secrets interactively.
# Usage: bash scripts/push_github_secrets.sh <owner/repo>
# Note: This will call 'gh secret set' for each non-empty input. gh must be authenticated.

set -euo pipefail

REPO="${1:-pentahexagon/universal-ai-orchestrator}"

echo "Setting secrets for $REPO (input values will be hidden)."
read -s -p "OPENAI_API_KEY: " OPENAI_API_KEY
echo
read -s -p "ANTHROPIC_API_KEY: " ANTHROPIC_API_KEY
echo
read -s -p "GEMINI_API_KEY: " GEMINI_API_KEY
echo
read -s -p "NOTION_API_KEY: " NOTION_API_KEY
echo
read -s -p "NOTION_DATABASE_ID: " NOTION_DATABASE_ID
echo

# Register secrets using gh CLI (will prompt for repo access if needed)
if [ -n "$OPENAI_API_KEY" ]; then
  gh secret set OPENAI_API_KEY --repo "$REPO" --body "$OPENAI_API_KEY"
fi
if [ -n "$ANTHROPIC_API_KEY" ]; then
  gh secret set ANTHROPIC_API_KEY --repo "$REPO" --body "$ANTHROPIC_API_KEY"
fi
if [ -n "$GEMINI_API_KEY" ]; then
  gh secret set GEMINI_API_KEY --repo "$REPO" --body "$GEMINI_API_KEY"
fi
if [ -n "$NOTION_API_KEY" ]; then
  gh secret set NOTION_API_KEY --repo "$REPO" --body "$NOTION_API_KEY"
fi
if [ -n "$NOTION_DATABASE_ID" ]; then
  gh secret set NOTION_DATABASE_ID --repo "$REPO" --body "$NOTION_DATABASE_ID"
fi

echo "Done. Secrets set for $REPO."