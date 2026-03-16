# OpenClaw Tools

OpenClaw 监控和管理工具集。

## 项目结构

```
openclaw_tools/
├── monitor/              # OpenClaw 监控面板
│   ├── api/              # Flask 后端 API
│   ├── static/           # 静态资源 (CSS/JS)
│   ├── templates/        # HTML 模板
│   ├── dev.sh            # 本地开发启动脚本
│   ├── start.sh          # 生产环境启动脚本
│   ├── publish.sh        # 发布脚本
│   └── requirements.txt  # Python 依赖
└── README.md
```

## 开发流程

### 1. 本地开发

```bash
# 启动本地开发环境 (端口 8081)
cd monitor
./dev.sh start

# 查看状态
./dev.sh status

# 查看日志
./dev.sh logs

# 停止服务
./dev.sh stop
```

本地开发地址: http://localhost:8081

### 2. 发布到生产环境

确认本地测试通过后：

```bash
# 发布（自动提交、推送、部署）
./publish.sh "你的提交信息"

# 或者直接运行（使用默认提交信息）
./publish.sh
```

生产环境地址: http://42.194.148.67:8080

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