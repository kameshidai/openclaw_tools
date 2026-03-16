# OpenClaw Monitor Skill

监控 OpenClaw 运行状态的 Web 面板，采用 Agent + UI 分离架构。

## 架构

```
本地服务器 (129.211.28.28)          目标服务器 (42.194.148.67)
┌─────────────────┐                ┌─────────────────┐
│ Monitor Agent   │──HTTP API──▶   │ Monitor UI      │
│ :9090           │                │ :8080           │
└─────────────────┘                └─────────────────┘
```

- 本地服务器：Monitor Agent (:9090) 提供 API
- 目标服务器：Monitor UI (:8080) 调用 Agent API

## 开发流程

1. `./agent.sh start` (本地启动 Agent)
2. `./dev.sh start` (开发 UI)
3. `MONITOR_AGENT_URL=http://129.211.28.28:9090 ./publish.sh` (发布)

## 端口与登录

| 服务 | 端口 |
|------|------|
| Agent API | 9090 |
| 开发 UI | 8081 |
| 生产 UI | 8080 |

**登录：** clawadmin / clawadmin123456

## 功能

- Gateway 状态监控 (9分钟自动更新)
- 智能体状态: 空闲(蓝) | 忙碌(绿) | 异常(红)
- 智能体别名: main→运维, sales→销售, finance→财务
- Gateway 重启 (需输入 checkok 确认)

## 访问地址

- 生产 UI: http://42.194.148.67:8080
- Agent API: http://129.211.28.28:9090/api/status
- 本地开发: http://localhost:8081

## 文件位置

- Skill: /root/.openclaw/skills/openclaw-monitor/
- 项目: /root/.openclaw/workspace-sales/openclaw_tools/monitor/
- 打包: openclaw-monitor.skill.tar.gz

## Systemd 服务

- 本地: openclaw-monitor-agent.service (端口 9090)
- 目标: openclaw-monitor.service (端口 8080)

## 性能优化

- Gateway 状态 9 分钟后台更新
- 端口检查代替命令行 (7.6s → 0.024s)
- 版本信息缓存 24h TTL