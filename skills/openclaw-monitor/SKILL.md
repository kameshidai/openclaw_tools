---
name: openclaw-monitor
description: OpenClaw 监控面板开发与部署。当用户提到 OpenClaw 监控、状态监控面板、远程监控 OpenClaw、创建监控 dashboard 时激活。支持：(1) 本地开发环境启动，(2) 发布到生产服务器，(3) Agent/UI 分离架构配置。
---

# OpenClaw Monitor

监控 OpenClaw 运行状态的 Web 面板，采用 Agent + UI 分离架构。

## 架构说明

```
┌─────────────────────────────────────────────────────────────┐
│  本地 OpenClaw 服务器                                       │
│  ┌─────────────────┐    ┌─────────────────┐                │
│  │ OpenClaw        │    │ Monitor Agent   │                │
│  │ (主服务)        │←───│ :9090           │←── 外网访问    │
│  └─────────────────┘    └─────────────────┘                │
└─────────────────────────────────────────────────────────────┘
                                    ↑
                                    │ HTTP API
                                    ↓
┌─────────────────────────────────────────────────────────────┐
│  目标服务器 (生产环境)                                       │
│  ┌─────────────────┐                                        │
│  │ Monitor UI      │                                        │
│  │ :8080           │                                        │
│  └─────────────────┘                                        │
└─────────────────────────────────────────────────────────────┘
```

**关键点：**
- **Agent** 运行在本地 OpenClaw 机器上，执行 `openclaw status` 等命令
- **UI** 运行在目标服务器上，通过 HTTP 调用 Agent API 获取数据
- 两者通过公网 IP 连接

## 项目结构

```
openclaw_tools/monitor/
├── agent/               # Agent 服务（本地）
│   └── app.py          # 状态 API 服务
├── api/                 # UI 后端（目标服务器）
│   └── app.py          # Web 服务
├── static/              # 静态资源
├── templates/           # HTML 模板
├── agent.sh             # Agent 启动脚本
├── dev.sh               # 本地开发脚本
├── start.sh             # 生产环境脚本
└── publish.sh           # 发布脚本
```

## 开发流程

### 1. 本地启动 Agent（必须）

Agent 提供状态 API，供 UI 调用：

```bash
cd openclaw_tools/monitor
./agent.sh start      # 启动 Agent (:9090)
./agent.sh status     # 查看状态
./agent.sh logs       # 查看日志
```

### 2. 本地开发测试

```bash
./dev.sh start        # 启动 Agent + UI (:8081)
./dev.sh status       # 查看状态
./dev.sh logs         # 查看日志
./dev.sh stop         # 停止服务
```

访问 http://localhost:8081

### 3. 发布到生产环境

```bash
# 设置 Agent URL 并发布
MONITOR_AGENT_URL=http://本地公网IP:9090 ./publish.sh "更新说明"
```

访问 http://目标服务器IP:8080

## 服务端口

| 服务 | 默认端口 | 环境变量 |
|------|---------|----------|
| Agent API | 9090 | MONITOR_AGENT_PORT |
| 开发 UI | 8081 | MONITOR_PORT |
| 生产 UI | 8080 | MONITOR_PORT |

## 配置说明

### 环境变量

- `MONITOR_AGENT_URL`: Agent API 地址（UI 需要配置）
- `MONITOR_PORT`: UI 端口
- `MONITOR_AGENT_PORT`: Agent 端口
- `MONITOR_DEBUG`: 开启调试模式 (true/false)
- `MONITOR_ENV`: 环境 (development/production)

### 获取本地公网 IP

```bash
curl -s ifconfig.me || curl -s ip.sb
```

### 检查 Agent 连通性

```bash
# 从目标服务器测试
curl http://本地公网IP:9090/health
```

## 登录信息

- 用户名: `clawadmin`
- 密码: `clawadmin123456`

## 故障排查

1. **UI 显示无法连接 Agent**
   - 检查 Agent 是否启动：`./agent.sh status`
   - 检查防火墙是否放行 9090 端口
   - 从目标服务器测试连通性

2. **数据不刷新**
   - Agent 可能超时，检查 `openclaw status` 命令是否正常
   - 查看日志：`./agent.sh logs`

3. **重启按钮无响应**
   - Agent 需要权限执行 `openclaw gateway restart`
   - 检查运行 Agent 的用户是否有权限