#!/bin/bash

# Greenbriar Telegram Bot 启动脚本

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# 检查 telegram_bot/.env 是否存在
if [ ! -f "telegram_bot/.env" ]; then
    echo "错误: telegram_bot/.env 不存在，请先运行 ./setup.sh 完成配置"
    exit 1
fi

# 检查 MCP 服务器 .env 是否存在
if [ ! -f "mcp-servers/google-workspace/.env" ]; then
    echo "错误: mcp-servers/google-workspace/.env 不存在，请先运行 ./setup.sh 完成配置"
    exit 1
fi

echo "启动 OpenCode Server..."
# 检查端口是否已被占用
if curl -s http://localhost:4096/global/health > /dev/null 2>&1; then
    echo "OpenCode Server 已在运行，复用现有实例"
    OPENCODE_PID=""
else
    # 必须在项目目录下启动，才能加载 opencode.json 和自定义 agents
    opencode serve --hostname 0.0.0.0 --port 4096 &
    OPENCODE_PID=$!

    # 等待 server 就绪
    echo "等待 OpenCode Server 启动..."
    STARTED=false
    for i in $(seq 1 15); do
        if curl -s http://localhost:4096/global/health > /dev/null 2>&1; then
            echo "OpenCode Server 已就绪"
            STARTED=true
            break
        fi
        sleep 1
    done

    if [ "$STARTED" = false ]; then
        echo "错误: OpenCode Server 启动超时，请检查日志"
        exit 1
    fi
fi

echo "启动 Telegram Bot..."
telegram_bot/venv/bin/python telegram_bot/opencode_bot.py

# Bot 退出后关闭 server（仅关闭本次启动的实例）
if [ -n "$OPENCODE_PID" ]; then
    kill $OPENCODE_PID 2>/dev/null
fi
