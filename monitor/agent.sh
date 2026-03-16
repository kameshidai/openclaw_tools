#!/bin/bash
# OpenClaw Monitor Agent 启动脚本
# 运行在 OpenClaw 所在机器上，提供状态 API

APP_DIR="/root/.openclaw/workspace-sales/openclaw_tools/monitor/agent"
LOG_FILE="/tmp/openclaw_monitor_agent.log"
PID_FILE="/tmp/openclaw_monitor_agent.pid"
PORT=${MONITOR_AGENT_PORT:-9090}

case "$1" in
    start)
        if [ -f "$PID_FILE" ] && kill -0 $(cat "$PID_FILE") 2>/dev/null; then
            echo "Monitor Agent 已在运行 (PID: $(cat $PID_FILE))"
            echo "API 地址: http://localhost:$PORT/api/status"
            exit 1
        fi
        
        echo "🦊 启动 Monitor Agent..."
        cd "$APP_DIR"
        export MONITOR_AGENT_PORT=$PORT
        nohup python3 app.py >> "$LOG_FILE" 2>&1 &
        echo $! > "$PID_FILE"
        sleep 1
        echo "✅ Monitor Agent 已启动 (PID: $(cat $PID_FILE))"
        echo "📍 API 地址: http://localhost:$PORT/api/status"
        echo "📋 日志文件: $LOG_FILE"
        ;;
        
    stop)
        if [ -f "$PID_FILE" ]; then
            PID=$(cat "$PID_FILE")
            if kill -0 "$PID" 2>/dev/null; then
                echo "🛑 停止 Monitor Agent (PID: $PID)..."
                kill "$PID"
                rm -f "$PID_FILE"
                echo "✅ 已停止"
            else
                echo "Monitor Agent 未运行"
                rm -f "$PID_FILE"
            fi
        else
            echo "Monitor Agent 未运行"
        fi
        ;;
        
    status)
        if [ -f "$PID_FILE" ] && kill -0 $(cat "$PID_FILE") 2>/dev/null; then
            echo "✅ Monitor Agent 正在运行 (PID: $(cat $PID_FILE))"
            echo "📍 API 地址: http://localhost:$PORT/api/status"
            curl -s http://localhost:$PORT/health | python3 -m json.tool 2>/dev/null || echo "健康检查失败"
        else
            echo "❌ Monitor Agent 未运行"
        fi
        ;;
        
    restart)
        $0 stop
        sleep 1
        $0 start
        ;;
        
    logs)
        tail -f "$LOG_FILE"
        ;;
        
    *)
        echo "用法: $0 {start|stop|status|restart|logs}"
        exit 1
        ;;
esac