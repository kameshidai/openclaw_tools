#!/bin/bash
# OpenClaw Monitor 发布脚本模板
# 用法: ./publish.sh ["commit message"]

set -e

# 配置 - 根据实际情况修改
REPO_DIR="${REPO_DIR:-.}"
REMOTE_HOST="${REMOTE_HOST:-app-server}"  # SSH alias
REMOTE_PATH="${REMOTE_PATH:-/home/ubuntu/openclaw_tools}"
AGENT_URL="${MONITOR_AGENT_URL:-http://localhost:9090}"

COMMIT_MSG="${1:-Update $(date +%Y-%m-%d\ %H:%M)}"

echo "=========================================="
echo "🚀 OpenClaw Monitor 发布流程"
echo "=========================================="

# 1. 提交本地更改
echo ""
echo "📦 [1/3] 提交代码到 GitHub..."
cd "$REPO_DIR"

if [ -n "$(git status --porcelain)" ]; then
    git add -A
    git commit -m "$COMMIT_MSG"
    git push
    echo "✅ 代码已推送到 GitHub"
else
    echo "ℹ️  没有待提交的更改"
fi

# 2. 服务器拉取最新代码
echo ""
echo "🔄 [2/3] 同步到生产服务器..."
ssh -o StrictHostKeyChecking=no "$REMOTE_HOST" \
    "cd $REMOTE_PATH && git pull"
echo "✅ 生产服务器代码已更新"

# 3. 重启生产服务
echo ""
echo "🦊 [3/3] 重启生产服务..."
ssh -o StrictHostKeyChecking=no "$REMOTE_HOST" \
    "MONITOR_AGENT_URL='$AGENT_URL' $REMOTE_PATH/monitor/start.sh restart"
echo "✅ 生产服务已重启"

echo ""
echo "=========================================="
echo "🎉 发布完成！"
echo "=========================================="
echo "📍 Agent URL: $AGENT_URL"
echo "📍 生产 UI: http://生产服务器IP:8080"
echo "=========================================="