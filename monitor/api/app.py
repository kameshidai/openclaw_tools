#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
OpenClaw Monitor UI
前端展示页面，从 Monitor Agent 获取数据
"""

import os
import requests
from datetime import datetime
from flask import Flask, jsonify, request, render_template, session
from flask_cors import CORS

# 获取正确的模板和静态文件路径
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE_DIR = os.path.join(BASE_DIR, 'templates')
STATIC_DIR = os.path.join(BASE_DIR, 'static')

app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)
app.secret_key = os.urandom(24)
CORS(app)

# 认证配置
ADMIN_USERNAME = "clawadmin"
ADMIN_PASSWORD = "clawadmin123456"

# Monitor Agent API 地址（本地 OpenClaw 服务器）
# 开发环境：localhost，生产环境：通过环境变量配置
MONITOR_AGENT_URL = os.environ.get('MONITOR_AGENT_URL', 'http://localhost:9090')

def get_agent_data():
    """从 Monitor Agent 获取数据"""
    try:
        response = requests.get(f"{MONITOR_AGENT_URL}/api/status", timeout=5)
        if response.status_code == 200:
            return response.json()
        return {"error": f"Agent returned {response.status_code}"}
    except requests.exceptions.ConnectionError:
        return {"error": "无法连接到 Monitor Agent", "agent_url": MONITOR_AGENT_URL}
    except requests.exceptions.Timeout:
        return {"error": "Monitor Agent 响应超时"}
    except Exception as e:
        return {"error": str(e)}

def restart_agent():
    """通过 Monitor Agent 重启 OpenClaw"""
    try:
        response = requests.post(f"{MONITOR_AGENT_URL}/api/restart", timeout=5)
        return response.json()
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username', '')
    password = data.get('password', '')
    
    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        session['logged_in'] = True
        return jsonify({"success": True, "message": "登录成功"})
    else:
        return jsonify({"success": False, "message": "用户名或密码错误"}), 401

@app.route('/api/logout', methods=['POST'])
def logout():
    session.pop('logged_in', None)
    return jsonify({"success": True, "message": "已登出"})

@app.route('/api/check-auth')
def check_auth():
    if session.get('logged_in'):
        return jsonify({"authenticated": True})
    return jsonify({"authenticated": False}), 401

@app.route('/api/status')
def status():
    """获取状态 - 从 Agent API 获取"""
    if not session.get('logged_in'):
        return jsonify({"error": "未登录"}), 401
    
    data = get_agent_data()
    
    # 添加 UI 层信息
    data['ui_timestamp'] = datetime.now().isoformat()
    data['agent_url'] = MONITOR_AGENT_URL
    
    return jsonify(data)

@app.route('/api/restart', methods=['POST'])
def restart():
    """重启 OpenClaw - 通过 Agent API"""
    if not session.get('logged_in'):
        return jsonify({"error": "未登录"}), 401
    
    result = restart_agent()
    return jsonify(result)

@app.route('/api/config')
def config():
    """获取配置信息"""
    if not session.get('logged_in'):
        return jsonify({"error": "未登录"}), 401
    
    return jsonify({
        "agent_url": MONITOR_AGENT_URL,
        "ui_version": "1.0.0"
    })

if __name__ == '__main__':
    port = int(os.environ.get('MONITOR_PORT', 8080))
    debug = os.environ.get('MONITOR_DEBUG', 'false').lower() == 'true'
    env = os.environ.get('MONITOR_ENV', 'production')
    
    print(f"🦊 OpenClaw Monitor UI starting...")
    print(f"   Environment: {env}")
    print(f"   Port: {port}")
    print(f"   Debug: {debug}")
    print(f"   Agent URL: {MONITOR_AGENT_URL}")
    
    app.run(host='0.0.0.0', port=port, debug=debug)