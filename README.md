# OpenClaw Tools

OpenClaw 监控和管理工具集。

## 架构说明

```
┌─────────────────────────────────────────────────────────────┐
│  本地 OpenClaw 服务器 (129.211.28.28)                        │
│  ┌─────────────────┐    ┌─────────────────┐                │
│  │ OpenClaw        │    │ Monitor Agent   │                │
│  │ (主服务)        │←───│ :9090           │←── 外网访问    │
│  └─────────────────┘    └─────────────────┘                │
└─────────────────────────────────────────────────────────────┘
                                    ↑
                                    │ HTTP API
                                    ↓
┌─────────────────────────────────────────────────────────────┐
│  目标服务器 (42.194.148.67)                                  │
│  ┌─────────────────┐                                        │
│  │ Monitor UI      │                                        │
│  │ :8080           │                                        │
│  └─────────────────┘                                        │
└─────────────────────────────────────────────────────────────┘
```

## 项目结构

```
openclaw_tools/
├── monitor/
│   ├── agent/              # Agent 服务（部署在本地）
│   ├── api/                # UI 后端服务（部署在目标服务器）
│   ├── static/             # 静态资源
│   ├── templates/          # HTML 模板
│   ├── agent.sh            # 本地 Agent 启动脚本
│   ├── dev.sh              # 本地开发启动脚本
│   ├── start.sh            # 生产环境启动脚本
│   └── publish.sh          # 发布脚本
└── README.md
```

## 部署步骤

### 1. 本地启动 Agent（必须）

```bash
# 启动本地 Agent（提供状态 API）
cd monitor
./agent.sh start

# 查看状态
./agent.sh status
```

### 2. 本地开发测试

```bash
# 启动本地开发环境（自动启动 Agent + UI）
./dev.sh start

# 访问 http://localhost:8081
```

### 3. 发布到生产环境

```bash
# 设置 Agent URL 并发布
MONITOR_AGENT_URL=http://129.211.28.28:9090 ./publish.sh "更新说明"
```

## 访问地址

| 服务 | 地址 | 说明 |
|------|------|------|
| 本地 Agent API | http://129.211.28.28:9090 | 提供 OpenClaw 状态数据 |
| 本地开发 UI | http://localhost:8081 | 开发测试用 |
| 生产 UI | http://42.194.148.67:8080 | 正式使用 |

## 登录信息

- **用户名**: clawadmin
- **密码**: clawadmin123456

## 功能特性

- ✅ 登录认证
- ✅ OpenClaw 版本和运行状态显示
- ✅ 智能体状态监控
- ✅ 系统指标 (CPU/内存/磁盘)
- ✅ 昼夜模式切换
- ✅ 每 2 分钟自动刷新
- ✅ 一键重启 OpenClaw

## Skill 文档

OpenClaw Monitor 流程已整理为 Skill: `openclaw-monitor`

位于: `/root/.openclaw/workspace-sales/openclaw-monitor.skill`