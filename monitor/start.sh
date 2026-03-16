#!/bin/bash
# OpenClaw Monitor 启动脚本

APP_DIR="/home/ubuntu/openclaw_tools/monitor/api"
LOG_FILE="/home/ubuntu/openclaw_tools/monitor/monitor.log"
PID_FILE="/tmp/openclaw_monitor.pid"

case "$1" in
    start)
        if [ -f "$PID_FILE" ] && kill -0 $(cat "$PID_FILE") 2>/dev/null; then
            echo "Monitor 已在运行 (PID: $(cat $PID_FILE))"
            exit 1
        fi
        
        echo "启动 OpenClaw Monitor..."
        cd "$APP_DIR"
        nohup python3 app.py >> "$LOG_FILE" 2>&1 &
        echo $! > "$PID_FILE"
        echo "Monitor 已启动 (PID: $!)，访问 http://$(hostname -I | awk '{print $1}'):8080"
        ;;
        
    stop)
        if [ -f "$PID_FILE" ]; then
            PID=$(cat "$PID_FILE")
            if kill -0 "$PID" 2>/dev/null; then
                echo "停止 Monitor (PID: $PID)..."
                kill "$PID"
                rm -f "$PID_FILE"
                echo "已停止"
            else
                echo "Monitor 未运行"
                rm -f "$PID_FILE"
            fi
        else
            echo "Monitor 未运行"
        fi
        ;;
        
    status)
        if [ -f "$PID_FILE" ] && kill -0 $(cat "$PID_FILE") 2>/dev/null; then
            echo "Monitor 正在运行 (PID: $(cat $PID_FILE))"
            echo "访问: http://$(hostname -I | awk '{print $1}'):8080"
        else
            echo "Monitor 未运行"
        fi
        ;;
        
    restart)
        $0 stop
        sleep 1
        $0 start
        ;;
        
    *)
        echo "用法: $0 {start|stop|status|restart}"
        exit 1
        ;;
esac