#!/bin/bash
# Greenbriar 一键配置脚本
# 检查依赖、配置 Telegram Bot Token、配置 Google OAuth

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# 颜色
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

ok()   { echo -e "${GREEN}[OK]${NC} $1"; }
warn() { echo -e "${YELLOW}[!!]${NC} $1"; }
err()  { echo -e "${RED}[ERR]${NC} $1"; }
info() { echo -e "${CYAN}[--]${NC} $1"; }
step() { echo -e "\n${BOLD}==> $1${NC}"; }

echo -e "${BOLD}"
echo "  ██████╗ ██████╗ ███████╗███████╗███╗   ██╗██████╗ ██████╗ ██╗ █████╗ ██████╗ "
echo "  ██╔════╝ ██╔══██╗██╔════╝██╔════╝████╗  ██║██╔══██╗██╔══██╗██║██╔══██╗██╔══██╗"
echo "  ██║  ███╗██████╔╝█████╗  █████╗  ██╔██╗ ██║██████╔╝██████╔╝██║███████║██████╔╝"
echo "  ██║   ██║██╔══██╗██╔══╝  ██╔══╝  ██║╚██╗██║██╔══██╗██╔══██╗██║██╔══██║██╔══██╗"
echo "  ╚██████╔╝██║  ██║███████╗███████╗██║ ╚████║██████╔╝██║  ██║██║██║  ██║██║  ██║"
echo "   ╚═════╝ ╚═╝  ╚═╝╚══════╝╚══════╝╚═╝  ╚═══╝╚═════╝ ╚═╝  ╚═╝╚═╝╚═╝  ╚═╝╚═╝  ╚═╝"
echo -e "${NC}"
echo "  日常事务 AI 助手 - 配置向导"
echo ""

ERRORS=0

# ─────────────────────────────────────────────────────────────
# 1. 系统依赖检查
# ─────────────────────────────────────────────────────────────
step "1. 系统依赖检查"

# Python 3
if command -v python3 &>/dev/null; then
    PY_VER=$(python3 --version 2>&1)
    ok "Python 3 已安装: $PY_VER"
else
    err "Python 3 未安装，请先安装 Python 3.10+"
    ERRORS=$((ERRORS+1))
fi

# opencode
if command -v opencode &>/dev/null; then
    ok "opencode 已安装: $(opencode --version 2>/dev/null || echo '版本未知')"
else
    err "opencode 未安装"
    info "安装方法: https://opencode.ai/docs/installation"
    ERRORS=$((ERRORS+1))
fi

# curl（start_bot.sh 健康检查用）
if command -v curl &>/dev/null; then
    ok "curl 已安装"
else
    warn "curl 未安装，start_bot.sh 的健康检查将跳过（不影响核心功能）"
fi

# ─────────────────────────────────────────────────────────────
# 2. Python 虚拟环境 & 依赖
# ─────────────────────────────────────────────────────────────
step "2. Python 依赖检查"

# Google Workspace MCP venv
GW_VENV="mcp-servers/google-workspace/venv"
GW_PYTHON="$GW_VENV/bin/python"
if [ -f "$GW_PYTHON" ]; then
    ok "google-workspace venv 已存在"
else
    info "创建 google-workspace venv..."
    python3 -m venv "$GW_VENV"
    ok "venv 已创建"
fi

# 检查核心包是否已安装
if "$GW_PYTHON" -c "import mcp, googleapiclient, google_auth_oauthlib, dotenv" 2>/dev/null; then
    ok "google-workspace 依赖已就绪"
else
    info "安装 google-workspace 依赖..."
    "$GW_VENV/bin/pip" install -q -r mcp-servers/google-workspace/requirements.txt
    ok "google-workspace 依赖安装完成"
fi

# Telegram Bot venv
TG_VENV="telegram_bot/venv"
TG_PYTHON="$TG_VENV/bin/python"
if [ -f "$TG_PYTHON" ]; then
    ok "telegram_bot venv 已存在"
else
    info "创建 telegram_bot venv..."
    python3 -m venv "$TG_VENV"
    ok "venv 已创建"
fi

if "$TG_PYTHON" -c "import telegram, requests, dotenv" 2>/dev/null; then
    ok "telegram_bot 依赖已就绪"
else
    info "安装 telegram_bot 依赖..."
    "$TG_VENV/bin/pip" install -q -r telegram_bot/requirements.txt
    ok "telegram_bot 依赖安装完成"
fi

# OpenCode 插件
if [ -d ".opencode/node_modules/@opencode-ai" ]; then
    ok "OpenCode 插件已安装"
else
    if command -v npm &>/dev/null; then
        info "安装 OpenCode 插件..."
        npm install --prefix .opencode --silent
        ok "OpenCode 插件安装完成"
    elif command -v bun &>/dev/null; then
        info "安装 OpenCode 插件（bun）..."
        bun install --cwd .opencode --silent
        ok "OpenCode 插件安装完成"
    else
        warn "npm/bun 均未找到，跳过 OpenCode 插件安装（可能影响某些功能）"
    fi
fi

# ─────────────────────────────────────────────────────────────
# 3. Telegram Bot Token 配置
# ─────────────────────────────────────────────────────────────
step "3. Telegram Bot Token 配置"

TG_ENV="telegram_bot/.env"

if [ -f "$TG_ENV" ]; then
    EXISTING_TOKEN=$(grep "^TELEGRAM_BOT_TOKEN=" "$TG_ENV" 2>/dev/null | cut -d'=' -f2-)
    if [ -n "$EXISTING_TOKEN" ] && [ "$EXISTING_TOKEN" != "your-telegram-bot-token-here" ]; then
        ok "Telegram Bot Token 已配置"
        SKIP_TG=true
    else
        warn "telegram_bot/.env 存在但 Token 未设置"
        SKIP_TG=false
    fi
else
    SKIP_TG=false
fi

if [ "$SKIP_TG" != "true" ]; then
    echo ""
    echo "  获取 Telegram Bot Token 的步骤："
    echo "  1. 在 Telegram 中找到 @BotFather"
    echo "  2. 发送 /newbot 创建新 bot"
    echo "  3. 按提示设置 bot 名称，获取 Token"
    echo ""
    read -p "  请输入 Telegram Bot Token（直接回车跳过）: " TG_TOKEN
    TG_TOKEN=$(echo "$TG_TOKEN" | tr -d ' ')

    if [ -n "$TG_TOKEN" ]; then
        # 验证 token 格式（数字:字母数字串）
        if echo "$TG_TOKEN" | grep -qE '^[0-9]+:[A-Za-z0-9_-]+$'; then
            # 写入 .env
            cp telegram_bot/.env.example "$TG_ENV"
            # 替换 token
            sed -i "s|TELEGRAM_BOT_TOKEN=.*|TELEGRAM_BOT_TOKEN=$TG_TOKEN|" "$TG_ENV"
            ok "Telegram Bot Token 已保存到 $TG_ENV"
        else
            warn "Token 格式看起来不对（应为 数字:字符串），已原样保存，请手动检查"
            cp telegram_bot/.env.example "$TG_ENV"
            sed -i "s|TELEGRAM_BOT_TOKEN=.*|TELEGRAM_BOT_TOKEN=$TG_TOKEN|" "$TG_ENV"
        fi
    else
        warn "跳过 Telegram Bot Token 配置"
        if [ ! -f "$TG_ENV" ]; then
            cp telegram_bot/.env.example "$TG_ENV"
        fi
        info "请稍后手动编辑 $TG_ENV 填入 TELEGRAM_BOT_TOKEN"
        ERRORS=$((ERRORS+1))
    fi
fi

# ─────────────────────────────────────────────────────────────
# 4. Google OAuth 配置
# ─────────────────────────────────────────────────────────────
step "4. Google OAuth 配置"

GW_ENV="mcp-servers/google-workspace/.env"

if [ -f "$GW_ENV" ]; then
    EXISTING_ID=$(grep "^GOOGLE_CLIENT_ID=" "$GW_ENV" 2>/dev/null | cut -d'=' -f2-)
    EXISTING_SECRET=$(grep "^GOOGLE_CLIENT_SECRET=" "$GW_ENV" 2>/dev/null | cut -d'=' -f2-)
    if [ -n "$EXISTING_ID" ] && [ "$EXISTING_ID" != "your-client-id-here.apps.googleusercontent.com" ] \
       && [ -n "$EXISTING_SECRET" ] && [ "$EXISTING_SECRET" != "your-client-secret-here" ]; then
        ok "Google OAuth 凭证已配置 (Client ID: ${EXISTING_ID:0:20}...)"
        SKIP_OAUTH=true
    else
        warn "google-workspace/.env 存在但凭证未设置"
        SKIP_OAUTH=false
    fi
else
    SKIP_OAUTH=false
fi

if [ "$SKIP_OAUTH" != "true" ]; then
    echo ""
    echo "  获取 Google OAuth 凭证的步骤："
    echo "  1. 访问 https://console.cloud.google.com/apis/credentials"
    echo "  2. 创建「OAuth 2.0 客户端 ID」，类型选「桌面应用」"
    echo "  3. 启用 Gmail API 和 Google Calendar API"
    echo "  4. 复制 Client ID 和 Client Secret"
    echo ""
    read -p "  请输入 Google Client ID（直接回车跳过）: " GOOG_ID
    GOOG_ID=$(echo "$GOOG_ID" | tr -d ' ')

    if [ -n "$GOOG_ID" ]; then
        read -p "  请输入 Google Client Secret: " GOOG_SECRET
        GOOG_SECRET=$(echo "$GOOG_SECRET" | tr -d ' ')

        if [ -n "$GOOG_SECRET" ]; then
            cp mcp-servers/google-workspace/.env.example "$GW_ENV"
            sed -i "s|GOOGLE_CLIENT_ID=.*|GOOGLE_CLIENT_ID=$GOOG_ID|" "$GW_ENV"
            sed -i "s|GOOGLE_CLIENT_SECRET=.*|GOOGLE_CLIENT_SECRET=$GOOG_SECRET|" "$GW_ENV"
            ok "Google OAuth 凭证已保存到 $GW_ENV"
        else
            warn "Client Secret 为空，跳过"
            cp mcp-servers/google-workspace/.env.example "$GW_ENV"
            info "请稍后手动编辑 $GW_ENV"
            ERRORS=$((ERRORS+1))
        fi
    else
        warn "跳过 Google OAuth 配置"
        if [ ! -f "$GW_ENV" ]; then
            cp mcp-servers/google-workspace/.env.example "$GW_ENV"
        fi
        info "请稍后手动编辑 $GW_ENV 填入凭证"
        ERRORS=$((ERRORS+1))
    fi
fi

# ─────────────────────────────────────────────────────────────
# 5. Google OAuth Token 检查 & 授权
# ─────────────────────────────────────────────────────────────
step "5. Google OAuth Token 检查 & 授权"

TOKEN_FILE="$HOME/.greenbriar/google_workspace_token.json"
GW_PYTHON="mcp-servers/google-workspace/venv/bin/python"
GW_ENV="mcp-servers/google-workspace/.env"

if [ -f "$TOKEN_FILE" ]; then
    ok "OAuth Token 已存在: $TOKEN_FILE"
    info "如需重新授权，删除该文件后重新运行 ./setup.sh"
else
    warn "OAuth Token 不存在，准备启动授权流程..."

    # 检查 .env 是否存在且凭证已填写
    if [ ! -f "$GW_ENV" ]; then
        err "找不到 $GW_ENV，请先完成上方 Google OAuth 配置"
        ERRORS=$((ERRORS+1))
    else
        GW_CLIENT_ID=$(grep "^GOOGLE_CLIENT_ID=" "$GW_ENV" 2>/dev/null | cut -d'=' -f2-)
        GW_CLIENT_SECRET=$(grep "^GOOGLE_CLIENT_SECRET=" "$GW_ENV" 2>/dev/null | cut -d'=' -f2-)

        if [ -z "$GW_CLIENT_ID" ] || [ "$GW_CLIENT_ID" = "your-client-id-here.apps.googleusercontent.com" ] \
        || [ -z "$GW_CLIENT_SECRET" ] || [ "$GW_CLIENT_SECRET" = "your-client-secret-here" ]; then
            err "Google OAuth 凭证未填写，请先完成上方第 4 步配置"
            ERRORS=$((ERRORS+1))
        else
            info "正在启动 Google OAuth 授权..."
            PYTHONPATH="mcp-servers/google-workspace" \
                "$GW_PYTHON" mcp-servers/google-workspace/auth_setup.py
            if [ $? -eq 0 ]; then
                ok "Google OAuth 授权完成，Token 已保存到 $TOKEN_FILE"
            else
                err "授权流程失败，请检查 Client ID / Client Secret 是否正确"
                ERRORS=$((ERRORS+1))
            fi
        fi
    fi
fi

# ─────────────────────────────────────────────────────────────
# 总结
# ─────────────────────────────────────────────────────────────
echo ""
echo -e "${BOLD}────────────────────────────────────────${NC}"
echo -e "${BOLD}配置摘要${NC}"
echo -e "${BOLD}────────────────────────────────────────${NC}"

if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}所有配置已就绪！${NC}"
    echo ""
    echo "启动方式："
    echo "  ./start_bot.sh        # 启动 OpenCode Server + Telegram Bot"
    echo "  opencode              # 仅启动交互式 CLI"
else
    echo -e "${YELLOW}有 $ERRORS 项配置待完成，请根据上方提示补全后再启动。${NC}"
    echo ""
    echo "配置文件位置："
    echo "  Telegram Token : telegram_bot/.env"
    echo "  Google OAuth   : mcp-servers/google-workspace/.env"
fi
echo ""
