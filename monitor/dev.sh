#!/bin/bash
# OpenClaw Monitor 本地开发环境启动脚本

APP_DIR="/root/.openclaw/workspace-sales/openclaw_tools/monitor/api"
LOG_FILE="/tmp/openclaw_monitor_dev.log"
PID_FILE="/tmp/openclaw_monitor_dev.pid"
PORT=8081

case "$1" in
    start)
        if [ -f "$PID_FILE" ] && kill -0 $(cat "$PID_FILE") 2>/dev/null; then
            echo "Dev Monitor 已在运行 (PID: $(cat $PID_FILE))"
            echo "访问: http://localhost:$PORT"
            exit 1
        fi
        
        echo "🚀 启动本地开发环境..."
        cd "$APP_DIR"
        export MONITOR_PORT=$PORT
        export MONITOR_DEBUG=true
        export MONITOR_ENV=development
        nohup python3 app.py >> "$LOG_FILE" 2>&1 &
        echo $! > "$PID_FILE"
        sleep 1
        echo "✅ Dev Monitor 已启动 (PID: $!)"
        echo "📍 访问地址: http://localhost:$PORT"
        echo "📋 日志文件: $LOG_FILE"
        ;;
        
    stop)
        if [ -f "$PID_FILE" ]; then
            PID=$(cat "$PID_FILE")
            if kill -0 "$PID" 2>/dev/null; then
                echo "🛑 停止 Dev Monitor (PID: $PID)..."
                kill "$PID"
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
            echo "✅ Dev Monitor 正在运行 (PID: $(cat $PID_FILE))"
            echo "📍 访问地址: http://localhost:$PORT"
        else
            echo "❌ Dev Monitor 未运行"
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