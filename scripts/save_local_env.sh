#!/usr/bin/env bash
# 안전한 .env 생성 스크립트 (터미널에서 실행)
# 사용법: bash scripts/save_local_env.sh

set -euo pipefail

read -p "Set OPENAI_API_KEY (leave blank to skip): " OPENAI_API_KEY
read -p "Set ANTHROPIC_API_KEY (leave blank to skip): " ANTHROPIC_API_KEY
read -p "Set GEMINI_API_KEY (leave blank to skip): " GEMINI_API_KEY
read -p "Set NOTION_API_KEY (leave blank to skip): " NOTION_API_KEY
read -p "Set NOTION_DATABASE_ID (leave blank to skip): " NOTION_DATABASE_ID

ENV_FILE=".env"

echo "Creating $ENV_FILE (will overwrite if exists). Do NOT commit this file to git."
cat > "$ENV_FILE" <<EOF
# Local environment file - DO NOT COMMIT
OPENAI_API_KEY=${OPENAI_API_KEY}
ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
GEMINI_API_KEY=${GEMINI_API_KEY}
NOTION_API_KEY=${NOTION_API_KEY}
NOTION_DATABASE_ID=${NOTION_DATABASE_ID}
EOF

# Restrict permissions
chmod 600 "$ENV_FILE"
echo "$ENV_FILE created with permissions 600."
