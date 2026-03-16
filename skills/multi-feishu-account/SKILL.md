---
name: multi-feishu-account
description: |
  多飞书账号管理 Skill。当用户提到飞书账号切换、多飞书通道、飞书账号配置时激活。
---

# Multi Feishu Account Skill

管理多个飞书账号的配置和切换。

## 当前配置

### 飞书账号

| 账号 ID | App ID | Bot 名称 | 用途 |
|---------|--------|----------|------|
| default | cli_a93cc6b467f81cd4 | 主账户 | 主账号 |
| account2 | cli_a93cc2573678dbdf | 账户2 | 备用 |
| account3 | cli_a93cf03f63789cc1 | 技能存储 | 文件存储 |

### Agent 绑定

| Agent ID | 飞书账号 |
|----------|----------|
| sales-assistant | account3 |

## 配置位置

配置文件：`~/.openclaw/openclaw.json`

```json
{
  "channels": {
    "feishu": {
      "enabled": true,
      "defaultAccount": "default",
      "connectionMode": "websocket",
      "accounts": {
        "default": {
          "appId": "cli_xxx",
          "appSecret": "xxx",
          "botName": "主账户"
        },
        "account2": {
          "appId": "cli_xxx",
          "appSecret": "xxx",
          "botName": "账户2"
        },
        "account3": {
          "appId": "cli_xxx",
          "appSecret": "xxx",
          "botName": "技能存储"
        }
      }
    }
  },
  "bindings": [
    {
      "agentId": "sales-assistant",
      "match": {
        "channel": "feishu",
        "accountId": "account3"
      }
    }
  ]
}
```

## 操作流程

### 1. 添加新飞书账号

```bash
# 编辑配置文件
vim ~/.openclaw/openclaw.json

# 在 accounts 中添加新账号
"account4": {
  "appId": "cli_xxx",
  "appSecret": "xxx",
  "botName": "新账号"
}
```

### 2. 绑定 Agent 到飞书账号

```json
{
  "agentId": "agent-name",
  "match": {
    "channel": "feishu",
    "accountId": "account4"
  }
}
```

### 3. 重启 Gateway

```bash
systemctl --user restart openclaw-gateway
```

### 4. 验证绑定

```bash
# 检查 Gateway 日志
journalctl --user -u openclaw-gateway -f
```

## 使用 feishu_doc 等工具时指定账号

当前 `feishu_doc` 工具默认使用 `default` 账号。

如需使用其他账号，需要：

1. 获取目标账号的 `tenant_access_token`
2. 使用 `curl` 直接调用飞书 API

```bash
# 获取 account3 的 token
APP_ID="cli_a93cf03f63789cc1"
APP_SECRET="xxx"

TOKEN=$(curl -s -X POST "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal" \
  -H "Content-Type: application/json" \
  -d "{\"app_id\":\"$APP_ID\",\"app_secret\":\"$APP_SECRET\"}" | jq -r '.tenant_access_token')

# 使用 token 操作文档
curl -s "https://open.feishu.cn/open-apis/docx/v1/documents/DOC_ID" \
  -H "Authorization: Bearer $TOKEN"
```

## 注意事项

1. 修改配置后必须重启 Gateway
2. `feishu_doc` 工具目前不支持动态切换账号
3. 每个飞书账号需要单独配置权限范围

## 相关文档

- 飞书开放平台：https://open.feishu.cn/
- OpenClaw 配置文档：https://docs.openclaw.ai/