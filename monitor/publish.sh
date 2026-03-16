#!/bin/bash
# OpenClaw Monitor 发布脚本
# 用法: ./publish.sh ["commit message"]

set -e

REPO_DIR="/root/.openclaw/workspace-sales/openclaw_tools"
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
ssh -o StrictHostKeyChecking=no app-server "cd /home/ubuntu/openclaw_tools && GIT_SSH_COMMAND='ssh -i ~/.ssh/id_github_proxy -o StrictHostKeyChecking=no' git pull"
echo "✅ 生产服务器代码已更新"

# 3. 重启生产服务
echo ""
echo "🦊 [3/3] 重启生产服务..."
ssh -o StrictHostKeyChecking=no app-server "/home/ubuntu/openclaw_tools/monitor/start.sh restart"
echo "✅ 生产服务已重启"

echo ""
echo "=========================================="
echo "🎉 发布完成！"
echo "=========================================="
echo "📍 生产环境: http://42.194.148.67:8080"
echo "📍 本地开发: http://localhost:8081 (运行 ./dev.sh start)"
echo "=========================================="