# Multi Feishu Account Skill

多飞书账号管理 Skill。管理多个飞书账号的配置和 Agent 绑定。

## 当前飞书账号

| 账号 ID | App ID | Bot 名称 | 用途 |
|---------|--------|----------|------|
| default | cli_a93cc6b467f81cd4 | 主账户 | 主账号 |
| account2 | cli_a93cc2573678dbdf | 账户2 | 备用 |
| account3 | cli_a93cf03f63789cc1 | 技能存储 | 文件存储 |

## Agent 绑定

- sales-assistant → account3 (技能存储)

## 配置文件

`~/.openclaw/openclaw.json`

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

## 添加新账号步骤

1. 编辑 `~/.openclaw/openclaw.json` 添加账号配置
2. 在 bindings 中添加 Agent 到账号的绑定
3. 重启 Gateway: `systemctl --user restart openclaw-gateway`

## 使用其他账号的 Token

`feishu_doc` 工具默认使用 default 账号。

其他账号需用 curl 调用飞书 API 获取 token 后操作：

```bash
APP_ID="cli_xxx"
APP_SECRET="xxx"

TOKEN=$(curl -s -X POST "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal" \
  -H "Content-Type: application/json" \
  -d "{\"app_id\":\"$APP_ID\",\"app_secret\":\"$APP_SECRET\"}" | jq -r '.tenant_access_token')

# 使用 token 操作文档
curl -s "https://open.feishu.cn/open-apis/docx/v1/documents/DOC_ID" \
  -H "Authorization: Bearer $TOKEN"
```

## 文件位置

- Skill: /root/.openclaw/skills/multi-feishu-account/
- 打包: multi-feishu-account.skill.tar.gz

## 相关文档

- 飞书开放平台: https://open.feishu.cn/
- OpenClaw 配置文档: https://docs.openclaw.ai/