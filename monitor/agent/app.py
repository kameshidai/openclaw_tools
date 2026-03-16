#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
OpenClaw Monitor Agent
运行在 OpenClaw 所在机器上，提供状态 API 供外网访问
"""

import os
import json
from datetime import datetime
from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def get_openclaw_version():
    """获取 OpenClaw 版本 - 从 package.json 读取"""
    try:
        import glob
        # 查找 openclaw package.json
        patterns = [
            "/root/.local/share/pnpm/global/*/node_modules/openclaw/package.json",
            "/usr/local/lib/node_modules/openclaw/package.json",
        ]
        for pattern in patterns:
            matches = glob.glob(pattern)
            if matches:
                with open(matches[0], 'r') as f:
                    data = json.load(f)
                    return f"OpenClaw {data.get('version', 'unknown')}"
        return "OpenClaw 2026.3.8"
    except:
        return "OpenClaw"

def get_gateway_status():
    """快速检查 Gateway 状态 - 通过端口检查"""
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('127.0.0.1', 31245))
        sock.close()
        return {
            "running": result == 0,
            "output": "Gateway port 31245 " + ("open" if result == 0 else "closed")
        }
    except:
        return {"running": False, "output": "Unable to check gateway port"}

def get_agents_status():
    """获取智能体状态 - 从工作目录读取"""
    agents = []
    try:
        workspace_dir = os.path.expanduser("~/.openclaw")
        for name in os.listdir(workspace_dir):
            if name.startswith("workspace-"):
                agent_name = name.replace("workspace-", "")
                agents.append({
                    "name": agent_name,
                    "status": "running",
                    "last_active": "recently"
                })
    except:
        pass
    
    # 如果没有找到，返回默认
    if not agents:
        agents = [
            {"name": "main", "status": "running", "last_active": "recently"},
            {"name": "sales", "status": "running", "last_active": "recently"}
        ]
    return agents

def get_system_metrics():
    """获取系统指标"""
    try:
        # CPU 使用率 - 快速读取
        cpu_usage = "0%"
        try:
            with open('/proc/stat', 'r') as f:
                line = f.readline()
            parts = line.split()[1:5]
            idle = int(parts[3])
            total = sum(int(x) for x in parts)
            cpu_usage = f"{100 - (idle * 100 // total if total > 0 else 0)}%"
        except:
            pass

        # 内存使用
        mem_total, mem_available = 0, 0
        try:
            with open('/proc/meminfo', 'r') as f:
                for line in f:
                    if line.startswith('MemTotal:'):
                        mem_total = int(line.split()[1]) // 1024
                    elif line.startswith('MemAvailable:'):
                        mem_available = int(line.split()[1]) // 1024
            mem_used = mem_total - mem_available
            mem_usage = f"{mem_used}/{mem_total} MB ({mem_used*100//mem_total if mem_total else 0}%)"
        except:
            mem_usage = "N/A"

        # 磁盘使用
        disk_usage = "N/A"
        try:
            import subprocess
            result = subprocess.run(["df", "-h", "/"], capture_output=True, text=True, timeout=2)
            for line in result.stdout.split('\n')[1:]:
                if line:
                    parts = line.split()
                    disk_usage = parts[4] if len(parts) >= 5 else "N/A"
                    break
        except:
            pass

        # 运行时间
        uptime = "N/A"
        try:
            with open('/proc/uptime', 'r') as f:
                seconds = int(float(f.read().split()[0]))
            days, remainder = divmod(seconds, 86400)
            hours, minutes = divmod(remainder, 3600)
            if days > 0:
                uptime = f"{days}d {hours}h"
            else:
                uptime = f"{hours}h {minutes//60}m"
        except:
            pass

        return {
            "cpu": cpu_usage,
            "memory": mem_usage,
            "disk": disk_usage,
            "uptime": uptime
        }
    except Exception as e:
        return {
            "cpu": "N/A",
            "memory": "N/A",
            "disk": "N/A",
            "uptime": "N/A",
            "error": str(e)
        }

@app.route('/health')
def health():
    """健康检查 - 快速响应"""
    return jsonify({"status": "ok", "timestamp": datetime.now().isoformat()})

@app.route('/api/status')
def status():
    """获取完整状态 - 供 Monitor UI 调用"""
    return jsonify({
        "version": get_openclaw_version(),
        "status": get_gateway_status(),
        "gateway": get_gateway_status(),
        "agents": get_agents_status(),
        "metrics": get_system_metrics(),
        "timestamp": datetime.now().isoformat(),
        "hostname": os.uname().nodename
    })

@app.route('/api/agents')
def agents():
    """仅获取智能体状态"""
    return jsonify(get_agents_status())

@app.route('/api/metrics')
def metrics():
    """仅获取系统指标"""
    return jsonify(get_system_metrics())

@app.route('/api/restart', methods=['POST'])
def restart():
    """重启 OpenClaw Gateway"""
    try:
        import subprocess
        subprocess.Popen(
            ["systemctl", "--user", "restart", "openclaw-gateway"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        return jsonify({"success": True, "message": "OpenClaw Gateway 重启中..."})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('MONITOR_AGENT_PORT', 9090))

    print(f"🦊 OpenClaw Monitor Agent starting on port {port}")
    print(f"📍 Status API: http://localhost:{port}/api/status")

    app.run(host='0.0.0.0', port=port, debug=False)