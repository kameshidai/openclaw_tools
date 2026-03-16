# MySkills - 自用 Skill 汇总

索引文档，点击链接查看各 Skill 详情。

---

## openclaw-monitor

**简介：** 监控 OpenClaw 运行状态的 Web 面板，Agent + UI 分离架构，支持 Gateway 状态监控和智能体状态展示。

**文档：** [skills/openclaw-monitor/README.md](./openclaw-monitor/README.md)

**下载：** [openclaw-monitor.skill.tar.gz](./openclaw-monitor.skill.tar.gz)

---

## multi-feishu-account

**简介：** 多飞书账号管理 Skill，管理多个飞书账号的配置和 Agent 绑定，支持添加新账号和切换账号。

**文档：** [skills/multi-feishu-account/README.md](./multi-feishu-account/README.md)

**下载：** [multi-feishu-account.skill.tar.gz](./multi-feishu-account.skill.tar.gz)

---

## 安装方法

```bash
# 下载 Skill
curl -o openclaw-monitor.skill.tar.gz \
  https://github.com/kameshidai/openclaw_tools/raw/main/skills/openclaw-monitor.skill.tar.gz

# 解压到 skills 目录
mkdir -p ~/.openclaw/skills/openclaw-monitor
tar -xzf openclaw-monitor.skill.tar.gz -C ~/.openclaw/skills/openclaw-monitor/
```

## 目录结构

```
skills/
├── openclaw-monitor/           # Skill 源码
│   ├── SKILL.md
│   ├── scripts/
│   └── references/
├── multi-feishu-account/       # Skill 源码
│   └── SKILL.md
├── openclaw-monitor.skill.tar.gz      # 打包文件
└── multi-feishu-account.skill.tar.gz  # 打包文件
```