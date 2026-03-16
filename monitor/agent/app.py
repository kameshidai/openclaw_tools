#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
OpenClaw Monitor Agent
运行在 OpenClaw 所在机器上，提供状态 API 供外网访问
"""

import subprocess
import json
import os
import re
from datetime import datetime
from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# API Key 认证（可选）
API_KEY = os.environ.get('MONITOR_API_KEY', 'openclaw-monitor-2024')

def check_api_key(request):
    """验证 API Key"""
    key = request.headers.get('X-API-Key', '')
    return key == API_KEY

def get_openclaw_status():
    """获取 OpenClaw 运行状态"""
    try:
        result = subprocess.run(
            ["openclaw", "gateway", "status"],
            capture_output=True,
            text=True,
            timeout=10
        )
        output = result.stdout + result.stderr
        return {
            "running": result.returncode == 0 or "running" in output.lower(),
            "output": output.strip(),
            "pid": None
        }
    except subprocess.TimeoutExpired:
        return {"running": True, "error": "timeout but gateway likely running"}
    except FileNotFoundError:
        return {"running": False, "error": "openclaw command not found"}
    except Exception as e:
        return {"running": False, "error": str(e)}

def get_openclaw_version():
    """获取 OpenClaw 版本"""
    try:
        result = subprocess.run(
            ["openclaw", "--version"],
            capture_output=True,
            text=True,
            timeout=3
        )
        if result.returncode == 0:
            return result.stdout.strip()
        return "Unknown"
    except:
        return "Unknown"

def get_agents_status():
    """获取智能体状态 - 通过 sessions_list API"""
    try:
        # 调用 OpenClaw 内置的会话列表
        result = subprocess.run(
            ["openclaw", "sessions", "list", "--json"],
            capture_output=True,
            text=True,
            timeout=5
        )

        agents = []
        if result.returncode == 0:
            try:
                data = json.loads(result.stdout)
                for session in data.get('sessions', []):
                    agents.append({
                        "name": session.get('label', session.get('agentId', 'unknown')),
                        "status": "running" if session.get('active') else "idle",
                        "last_active": session.get('lastActivity', 'unknown'),
                        "model": session.get('model', 'unknown')
                    })
            except json.JSONDecodeError:
                pass

        # 如果无法获取，尝试从目录读取
        if not agents:
            workspace_dir = os.path.expanduser("~/.openclaw")
            for name in os.listdir(workspace_dir):
                if name.startswith("workspace-"):
                    agents.append({
                        "name": name.replace("workspace-", ""),
                        "status": "running",
                        "last_active": "recently"
                    })

        return agents if agents else [
            {"name": "sales-assistant", "status": "running", "last_active": "recently"}
        ]
    except Exception as e:
        return [{"name": "error", "status": "error", "last_active": str(e)}]

def get_system_metrics():
    """获取系统指标"""
    try:
        # CPU 使用率
        cpu_usage = "0%"
        try:
            with open('/proc/stat', 'r') as f:
                line = f.readline()
            # 简化的 CPU 计算
            parts = line.split()[1:5]
            idle = int(parts[3])
            total = sum(int(x) for x in parts)
            cpu_usage = f"{100 - (idle * 100 // total if total > 0 else 0)}%"
        except:
            pass

        # 内存使用
        mem_total, mem_used, mem_available = 0, 0, 0
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
            result = subprocess.run(["df", "-h", "/"], capture_output=True, text=True, timeout=3)
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

def get_gateway_info():
    """获取 Gateway 信息"""
    try:
        result = subprocess.run(
            ["openclaw", "gateway", "status"],
            capture_output=True,
            text=True,
            timeout=5
        )
        return {
            "output": result.stdout.strip(),
            "running": "running" in result.stdout.lower() or result.returncode == 0
        }
    except:
        return {"running": False, "output": "Unable to get gateway status"}

@app.route('/health')
def health():
    """健康检查"""
    return jsonify({"status": "ok", "timestamp": datetime.now().isoformat()})

@app.route('/api/status')
def status():
    """获取完整状态 - 供 Monitor UI 调用"""
    # API Key 验证（可选，可以注释掉）
    # if not check_api_key(request):
    #     return jsonify({"error": "Unauthorized"}), 401

    return jsonify({
        "version": get_openclaw_version(),
        "status": get_openclaw_status(),
        "gateway": get_gateway_info(),
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
        subprocess.Popen(
            ["openclaw", "gateway", "restart"],
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