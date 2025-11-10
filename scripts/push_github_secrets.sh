#!/usr/bin/env bash
# GitHub Secrets에 API 키를 등록하는 스크립트
# 사용법: bash scripts/push_github_secrets.sh
# 필요: gh CLI 설치 및 로그인 (gh auth login)

set -euo pipefail

echo "Pushing secrets to GitHub repository..."
echo "Make sure you are logged in with gh CLI: gh auth status"
echo ""

read -p "Set OPENAI_API_KEY (leave blank to skip): " OPENAI_API_KEY
read -p "Set ANTHROPIC_API_KEY (leave blank to skip): " ANTHROPIC_API_KEY
read -p "Set GEMINI_API_KEY (leave blank to skip): " GEMINI_API_KEY
read -p "Set NOTION_API_KEY (leave blank to skip): " NOTION_API_KEY
read -p "Set NOTION_DATABASE_ID (leave blank to skip): " NOTION_DATABASE_ID

echo ""
echo "Uploading secrets to GitHub repository..."

if [[ -n "$OPENAI_API_KEY" ]]; then
  echo "$OPENAI_API_KEY" | gh secret set OPENAI_API_KEY
  echo "✓ OPENAI_API_KEY set"
fi

if [[ -n "$ANTHROPIC_API_KEY" ]]; then
  echo "$ANTHROPIC_API_KEY" | gh secret set ANTHROPIC_API_KEY
  echo "✓ ANTHROPIC_API_KEY set"
fi

if [[ -n "$GEMINI_API_KEY" ]]; then
  echo "$GEMINI_API_KEY" | gh secret set GEMINI_API_KEY
  echo "✓ GEMINI_API_KEY set"
fi

if [[ -n "$NOTION_API_KEY" ]]; then
  echo "$NOTION_API_KEY" | gh secret set NOTION_API_KEY
  echo "✓ NOTION_API_KEY set"
fi

if [[ -n "$NOTION_DATABASE_ID" ]]; then
  echo "$NOTION_DATABASE_ID" | gh secret set NOTION_DATABASE_ID
  echo "✓ NOTION_DATABASE_ID set"
fi

echo ""
echo "✅ Secrets uploaded to GitHub repository"
echo "View secrets: gh secret list"
