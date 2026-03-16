#!/bin/bash
# sync-skill.sh - 更新 Skill 并同步到 GitHub
# 用法: ./sync-skill.sh <skill-name> [commit-message]
# 示例: ./sync-skill.sh openclaw-monitor "添加新功能"

set -e

SKILL_NAME="$1"
COMMIT_MSG="${2:-Update $SKILL_NAME}"

if [ -z "$SKILL_NAME" ]; then
    echo "用法: $0 <skill-name> [commit-message]"
    echo "可用的 Skill:"
    ls -1 /root/.openclaw/skills/ 2>/dev/null || echo "  (无)"
    exit 1
fi

SKILL_DIR="/root/.openclaw/skills/$SKILL_NAME"
WORKSPACE="/root/.openclaw/workspace-sales/openclaw_tools"

if [ ! -d "$SKILL_DIR" ]; then
    echo "❌ Skill 不存在: $SKILL_DIR"
    exit 1
fi

echo "=== 同步 Skill: $SKILL_NAME ==="

# 1. 打包 Skill
echo "📦 打包 Skill..."
cd "$SKILL_DIR"
tar -czf "/tmp/${SKILL_NAME}.skill.tar.gz" ./*
echo "   → /tmp/${SKILL_NAME}.skill.tar.gz"

# 2. 复制打包文件
echo "📋 复制到仓库..."
mkdir -p "$WORKSPACE/skills"
cp "/tmp/${SKILL_NAME}.skill.tar.gz" "$WORKSPACE/skills/"

# 3. 同步 Skill 源码
echo "📁 同步源码..."
mkdir -p "$WORKSPACE/skills/$SKILL_NAME"
cp -r "$SKILL_DIR"/* "$WORKSPACE/skills/$SKILL_NAME/"

# 4. 检查是否有 README.md
if [ ! -f "$WORKSPACE/skills/$SKILL_NAME/README.md" ] && [ -f "$SKILL_DIR/SKILL.md" ]; then
    echo "📝 创建 README.md..."
    cp "$SKILL_DIR/SKILL.md" "$WORKSPACE/skills/$SKILL_NAME/README.md"
fi

# 5. Git 操作
echo "🚀 提交到 GitHub..."
cd "$WORKSPACE"
git add "skills/$SKILL_NAME/" "skills/${SKILL_NAME}.skill.tar.gz"
git commit -m "$COMMIT_MSG"
git push origin main

echo ""
echo "✅ 同步完成！"
echo "   GitHub: https://github.com/kameshidai/openclaw_tools/tree/main/skills/$SKILL_NAME"
echo "   下载: https://github.com/kameshidai/openclaw_tools/raw/main/skills/${SKILL_NAME}.skill.tar.gz"