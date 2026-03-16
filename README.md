# OpenClaw Tools

OpenClaw 监控和管理工具集。

## 架构说明

```
┌─────────────────────────────────────────────────────────────┐
│  本地 OpenClaw 服务器 (当前机器)                              │
│  ┌─────────────────┐    ┌─────────────────┐                │
│  │ OpenClaw        │    │ Monitor Agent   │                │
│  │ (主服务)        │←───│ (:9090)         │←─── 外网访问    │
│  └─────────────────┘    └─────────────────┘                │
└─────────────────────────────────────────────────────────────┘
                                    ↑
                                    │ HTTP API
                                    ↓
┌─────────────────────────────────────────────────────────────┐
│  目标服务器 (42.194.148.67)                                  │
│  ┌─────────────────┐                                        │
│  │ Monitor UI     │                                        │
│  │ (:8080)        │                                        │
│  └─────────────────┘                                        │
└─────────────────────────────────────────────────────────────┘
```

- **Monitor Agent**: 运行在本地 OpenClaw 机器上，提供状态 API（端口 9090）
- **Monitor UI**: 运行在目标服务器上，从 Agent 获取数据并展示

## 项目结构

```
openclaw_tools/
├── monitor/              # OpenClaw 监控面板
│   ├── agent/            # Agent API 服务（部署在本地）
│   ├── api/              # UI 后端服务（部署在目标服务器）
│   ├── static/           # 静态资源
│   ├── templates/        # HTML 模板
│   ├── agent.sh          # 本地 Agent 启动脚本
│   ├── dev.sh            # 本地开发启动脚本
│   ├── start.sh          # 生产环境启动脚本
│   └── publish.sh        # 发布脚本
└── README.md
```

## 部署步骤

### 1. 本地启动 Agent（必须）

```bash
# 启动本地 Agent（提供状态 API）
./monitor/agent.sh start

# 查看状态
./monitor/agent.sh status
```

Agent 会在端口 9090 上启动。

### 2. 本地开发测试

```bash
# 启动本地开发环境（自动启动 Agent + UI）
cd monitor
./dev.sh start

# 访问 http://localhost:8081
```

### 3. 发布到生产环境

确认本地测试通过后，配置 Agent URL 并发布：

```bash
# 方式1: 设置环境变量后发布
MONITOR_AGENT_URL=http://你的本地IP:9090 ./publish.sh "更新说明"

# 方式2: SSH 到目标服务器手动配置
ssh app-server
MONITOR_AGENT_URL=http://你的本地IP:9090 /home/ubuntu/openclaw_tools/monitor/start.sh start
```

## 访问地址

| 服务 | 地址 | 说明 |
|------|------|------|
| 本地 Agent API | http://localhost:9090/api/status | 提供 OpenClaw 状态数据 |
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