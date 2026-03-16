#!/bin/bash
# OpenClaw Monitor 本地开发环境启动脚本
# 本地开发时：Agent 和 UI 都在同一台机器上

APP_DIR="/root/.openclaw/workspace-sales/openclaw_tools/monitor/api"
AGENT_DIR="/root/.openclaw/workspace-sales/openclaw_tools/monitor/agent"
LOG_FILE="/tmp/openclaw_monitor_dev.log"
PID_FILE="/tmp/openclaw_monitor_dev.pid"
PORT=8081
AGENT_PORT=9090

case "$1" in
    start)
        if [ -f "$PID_FILE" ] && kill -0 $(cat "$PID_FILE") 2>/dev/null; then
            echo "Dev Monitor 已在运行 (PID: $(cat $PID_FILE))"
            echo "UI: http://localhost:$PORT"
            exit 1
        fi
        
        echo "🚀 启动本地开发环境..."
        
        # 先启动 Agent
        echo "   启动 Monitor Agent (端口 $AGENT_PORT)..."
        cd "$AGENT_DIR"
        export MONITOR_AGENT_PORT=$AGENT_PORT
        nohup python3 app.py >> "$LOG_FILE" 2>&1 &
        AGENT_PID=$!
        sleep 1
        
        # 再启动 UI
        echo "   启动 Monitor UI (端口 $PORT)..."
        cd "$APP_DIR"
        export MONITOR_PORT=$PORT
        export MONITOR_DEBUG=true
        export MONITOR_ENV=development
        export MONITOR_AGENT_URL="http://localhost:$AGENT_PORT"
        nohup python3 app.py >> "$LOG_FILE" 2>&1 &
        UI_PID=$!
        
        echo $UI_PID > "$PID_FILE"
        sleep 1
        echo "✅ Dev Monitor 已启动"
        echo "📍 UI 地址: http://localhost:$PORT"
        echo "📍 Agent API: http://localhost:$AGENT_PORT/api/status"
        echo "📋 日志文件: $LOG_FILE"
        ;;
        
    stop)
        if [ -f "$PID_FILE" ]; then
            PID=$(cat "$PID_FILE")
            if kill -0 "$PID" 2>/dev/null; then
                echo "🛑 停止 Dev Monitor..."
                kill "$PID"
                # 也停止 agent
                pkill -f "monitor/agent/app.py" 2>/dev/null || true
                rm -f "$PID_FILE"
                echo "✅ 已停止"
            else
                echo "Dev Monitor 未运行"
                rm -f "$PID_FILE"
            fi
        else
            echo "Dev Monitor 未运行"
        fi
        ;;
        
    status)
        if [ -f "$PID_FILE" ] && kill -0 $(cat "$PID_FILE") 2>/dev/null; then
            echo "✅ Dev Monitor 正在运行"
            echo "📍 UI: http://localhost:$PORT"
            echo "📍 Agent: http://localhost:$AGENT_PORT/api/status"
        else
            echo "❌ Dev Monitor 未运行"
        fi
        ;;
        
    restart)
        $0 stop
        sleep 2
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