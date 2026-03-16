#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
OpenClaw Monitor Agent
运行在 OpenClaw 所在机器上，提供状态 API 供外网访问
"""

import os
import json
import socket
import time
import threading
from datetime import datetime
from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# 配置
CACHE_DIR = os.path.expanduser("~/.openclaw/monitor_cache")
CACHE_FILE = os.path.join(CACHE_DIR, "status_cache.json")
GATEWAY_UPDATE_INTERVAL = 9 * 60  # 9分钟
CACHE_DURATION = 15 * 60  # 15分钟

# 全局状态缓存
status_cache = {
    "version": "OpenClaw",
    "gateway": {"running": False, "output": ""},
    "last_update": 0
}
cache_lock = threading.Lock()

def ensure_cache_dir():
    """确保缓存目录存在"""
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR)

def save_cache():
    """保存缓存到文件"""
    try:
        ensure_cache_dir()
        with open(CACHE_FILE, 'w') as f:
            json.dump(status_cache, f, indent=2)
    except:
        pass

def load_cache():
    """从文件加载缓存"""
    try:
        if os.path.exists(CACHE_FILE):
            with open(CACHE_FILE, 'r') as f:
                return json.load(f)
    except:
        pass
    return None

def get_openclaw_version():
    """获取 OpenClaw 版本 - 从缓存或读取"""
    global status_cache
    
    with cache_lock:
        if status_cache.get("version") and status_cache.get("version") != "OpenClaw":
            return status_cache["version"]
    
    # 重新获取
    version = "OpenClaw"
    try:
        import glob
        patterns = [
            "/root/.local/share/pnpm/global/*/node_modules/openclaw/package.json",
            "/usr/local/lib/node_modules/openclaw/package.json",
        ]
        for pattern in patterns:
            matches = glob.glob(pattern)
            if matches:
                with open(matches[0], 'r') as f:
                    data = json.load(f)
                    version = f"OpenClaw {data.get('version', 'unknown')}"
                    break
    except:
        pass
    
    with cache_lock:
        status_cache["version"] = version
    
    save_cache()
    return version

def check_gateway_port():
    """检查 Gateway 端口"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('127.0.0.1', 31245))
        sock.close()
        return result == 0
    except:
        return False

def update_gateway_status():
    """后台任务：更新 Gateway 状态"""
    global status_cache
    
    print("🔄 正在更新 Gateway 状态...")
    
    is_running = check_gateway_port()
    
    with cache_lock:
        status_cache["gateway"] = {
            "running": is_running,
            "output": "Gateway port 31245 " + ("open" if is_running else "closed")
        }
        status_cache["last_update"] = time.time()
    
    save_cache()
    print(f"✅ Gateway 状态已更新: {'running' if is_running else 'stopped'}")

def get_gateway_status():
    """获取 Gateway 状态 - 从缓存"""
    global status_cache
    
    current_time = time.time()
    
    with cache_lock:
        # 检查是否需要更新
        if current_time - status_cache.get("last_update", 0) > GATEWAY_UPDATE_INTERVAL:
            # 返回旧数据，同时触发后台更新
            threading.Thread(target=update_gateway_status, daemon=True).start()
        
        return status_cache.get("gateway", {"running": False, "output": "Not initialized"})

def get_agents_status():
    """获取智能体状态 - 从工作目录读取"""
    # 智能体别名映射
    ALIAS_MAP = {
        "main": "运维",
        "sales": "销售",
        "finance": "财务"
    }
    
    agents = []
    try:
        workspace_dir = os.path.expanduser("~/.openclaw")
        for name in os.listdir(workspace_dir):
            if name.startswith("workspace-"):
                agent_name = name.replace("workspace-", "")
                alias = ALIAS_MAP.get(agent_name, agent_name)
                agents.append({
                    "name": agent_name,
                    "alias": alias,
                    "status": "running",
                    "last_active": "recently"
                })
    except:
        pass
    
    if not agents:
        agents = [
            {"name": "main", "alias": "运维", "status": "running", "last_active": "recently"}
        ]
    return agents

def get_system_metrics():
    """获取系统指标"""
    try:
        # CPU
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

        # 内存
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

        # 磁盘
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
            uptime = f"{days}d {hours}h" if days > 0 else f"{hours}h {minutes//60}m"
        except:
            pass

        return {"cpu": cpu_usage, "memory": mem_usage, "disk": disk_usage, "uptime": uptime}
    except:
        return {"cpu": "N/A", "memory": "N/A", "disk": "N/A", "uptime": "N/A"}

# 初始化时加载缓存
cached = load_cache()
if cached:
    with cache_lock:
        status_cache = cached
    print(f"📦 已加载缓存，上次更新: {datetime.fromtimestamp(status_cache.get('last_update', 0))}")

# 启动时立即更新一次 Gateway 状态
update_gateway_status()

@app.route('/health')
def health():
    return jsonify({"status": "ok", "timestamp": datetime.now().isoformat()})

@app.route('/api/status')
def status():
    """获取完整状态"""
    with cache_lock:
        last_update = status_cache.get("last_update", 0)
    
    return jsonify({
        "version": get_openclaw_version(),
        "status": status_cache.get("gateway", {}),
        "gateway": status_cache.get("gateway", {}),
        "agents": get_agents_status(),
        "metrics": get_system_metrics(),
        "timestamp": datetime.now().isoformat(),
        "last_gateway_update": datetime.fromtimestamp(last_update).isoformat(),
        "hostname": os.uname().nodename
    })

@app.route('/api/agents')
def agents():
    return jsonify(get_agents_status())

@app.route('/api/metrics')
def metrics():
    return jsonify(get_system_metrics())

@app.route('/api/gateway-update', methods=['POST'])
def manual_update():
    """手动触发 Gateway 状态更新"""
    threading.Thread(target=update_gateway_status, daemon=True).start()
    return jsonify({"success": True, "message": "正在更新..."})

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
        # 立即更新状态
        threading.Thread(target=update_gateway_status, daemon=True).start()
        return jsonify({"success": True, "message": "OpenClaw Gateway 重启中..."})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/cache/clear', methods=['POST'])
def clear_cache():
    try:
        if os.path.exists(CACHE_FILE):
            os.remove(CACHE_FILE)
        return jsonify({"success": True, "message": "缓存已清除"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('MONITOR_AGENT_PORT', 9090))

    print(f"🦊 OpenClaw Monitor Agent starting on port {port}")
    print(f"📍 Status API: http://localhost:{port}/api/status")
    print(f"⏱️ Gateway 更新间隔: {GATEWAY_UPDATE_INTERVAL//60} 分钟")

    app.run(host='0.0.0.0', port=port, debug=False)