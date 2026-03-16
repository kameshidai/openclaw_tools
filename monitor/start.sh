#!/bin/bash
# OpenClaw Monitor 生产环境启动脚本
# 运行在目标服务器上，从远程 Agent API 获取数据

APP_DIR="/home/ubuntu/openclaw_tools/monitor/api"
LOG_FILE="/home/ubuntu/openclaw_tools/monitor/monitor.log"
PID_FILE="/tmp/openclaw_monitor.pid"
PORT=8080

# Agent API 地址（本地 OpenClaw 服务器）
# 需要根据实际情况修改
AGENT_URL=${MONITOR_AGENT_URL:-"http://localhost:9090"}

case "$1" in
    start)
        if [ -f "$PID_FILE" ] && kill -0 $(cat "$PID_FILE") 2>/dev/null; then
            echo "Monitor 已在运行 (PID: $(cat $PID_FILE))"
            exit 1
        fi
        
        echo "启动 OpenClaw Monitor..."
        cd "$APP_DIR"
        export MONITOR_PORT=$PORT
        export MONITOR_AGENT_URL="$AGENT_URL"
        nohup python3 app.py >> "$LOG_FILE" 2>&1 &
        echo $! > "$PID_FILE"
        echo "Monitor 已启动 (PID: $!)，访问 http://$(hostname -I | awk '{print $1}'):8080"
        echo "Agent URL: $AGENT_URL"
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
        AGENT_URL="$AGENT_URL" $0 start
        ;;
        
    *)
        echo "用法: $0 {start|stop|status|restart}"
        exit 1
        ;;
esac