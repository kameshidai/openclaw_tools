---
name: multi-feishu-account
description: |
  多飞书账号管理 Skill。当用户提到飞书账号切换、多飞书通道、飞书账号配置、绑定用户时激活。
---

# Multi Feishu Account Skill

多飞书账号管理 Skill。管理多个飞书账号的配置、用户绑定和 Agent 绑定。

## 核心功能

### 1. 多账号管理

支持多个飞书账号的配置和切换。

### 2. 用户绑定机制

**绑定规则：**
- 每个飞书通道必须绑定用户 ID
- 非绑定用户发送的消息将被忽略
- 绑定关系：`agentId` + `channel` + `accountId` + `userId`

### 3. 换绑验证

- 换绑需要验证码
- 验证码：`changefeishu_2026`
- **仅 main 智能体可查询和回复验证码**
- 子智能体不能查询或回复验证码

## 当前配置

### 飞书账号

| 账号 ID | App ID | Bot 名称 | 用途 |
|---------|--------|----------|------|
| default | cli_a93cc6b467f81cd4 | 主账户 | 主账号 |
| account2 | cli_a93cc2573678dbdf | 账户2 | 备用 |
| account3 | cli_a93cf03f63789cc1 | 技能存储 | 文件存储 |

### Agent 绑定（含用户绑定）

| Agent ID | 飞书账号 | 绑定用户 ID |
|----------|----------|-------------|
| sales-assistant | account3 | ou_bbd25153eb301e9665253b7e10d116ce |

## 配置文件

### 主配置文件

`~/.openclaw/openclaw.json` - 系统配置，包含账号和绑定：

```json
{
  "channels": {
    "feishu": {
      "enabled": true,
      "defaultAccount": "default",
      "connectionMode": "websocket",
      "accounts": {
        "default": { "appId": "cli_xxx", "appSecret": "xxx", "botName": "主账户" },
        "account2": { "appId": "cli_xxx", "appSecret": "xxx", "botName": "账户2" },
        "account3": { "appId": "cli_xxx", "appSecret": "xxx", "botName": "技能存储" }
      }
    }
  },
  "bindings": [
    {
      "agentId": "sales-assistant",
      "match": { "channel": "feishu", "accountId": "account3" },
      "userId": "ou_xxxxxxxxxxxxxxxxxxxxxxxx"
    }
  ]
}
```

### 绑定规则文件

`~/.openclaw/feishu_bindings.json` - 绑定规则和验证码（不影响系统运行）：

```json
{
  "description": "飞书通道用户绑定规则",
  "rules": [
    "每个飞书通道必须绑定用户ID",
    "非绑定用户的消息将被忽略",
    "换绑需要验证码"
  ],
  "verificationCode": "changefeishu_2026",
  "codeAccess": ["main"],
  "note": "子智能体不能查询或回复验证码"
}
```

## 添加新绑定步骤

### 1. 添加账号配置

```bash
vim ~/.openclaw/openclaw.json
```

在 `accounts` 中添加新账号：

```json
"account4": {
  "appId": "cli_xxx",
  "appSecret": "xxx",
  "botName": "新账号"
}
```

### 2. 添加 Agent + 用户绑定

在 `bindings` 中添加：

```json
{
  "agentId": "agent-name",
  "match": {
    "channel": "feishu",
    "accountId": "account4"
  },
  "userId": "ou_xxxxxxxxxxxxxxxxxxxxxxxx"
}
```

### 3. 重启 Gateway

```bash
systemctl --user restart openclaw-gateway
```

### 4. 验证绑定

```bash
# 检查绑定状态
curl http://localhost:31245/api/status
```

## 换绑流程

1. 用户请求换绑
2. **main 智能体验证验证码**（`changefeishu_2026`）
3. 验证通过后更新 `userId`
4. 重启 Gateway

**安全规则：**
- 子智能体不能查询验证码
- 子智能体不能回复验证码
- 只有 main 智能体可以处理换绑请求

## 消息过滤逻辑

```
收到消息
  ├── 获取 sender_id (userId)
  ├── 查找该 channel 的绑定配置
  ├── 比对 userId
  │   ├── 匹配 → 处理消息
  │   └── 不匹配 → 忽略 (HEARTBEAT_OK)
  └── 未绑定 → 忽略
```

## 文件位置

- Skill: /root/.openclaw/skills/multi-feishu-account/
- 打包: multi-feishu-account.skill.tar.gz
- GitHub: https://github.com/kameshidai/openclaw_tools/tree/main/skills/multi-feishu-account

## 相关文档

- 飞书开放平台: https://open.feishu.cn/
- OpenClaw 配置文档: https://docs.openclaw.ai/