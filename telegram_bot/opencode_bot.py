import os
import logging
import requests
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

OPENCODE_SERVER = os.getenv("OPENCODE_SERVER", "http://127.0.0.1:4096")
OPENCODE_PASSWORD = os.getenv("OPENCODE_SERVER_PASSWORD", "")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "")

session_id = None

def get_session():
    global session_id
    if session_id:
        return session_id
    
    response = requests.post(
        f"{OPENCODE_SERVER}/session",
        json={"title": "Telegram Session"}
    )
    if response.status_code == 200:
        session_id = response.json()["id"]
        return session_id
    return None

def send_message_to_opencode(message: str) -> str:
    session = get_session()
    if not session:
        return "无法创建 OpenCode 会话"
    
    auth = ("opencode", OPENCODE_PASSWORD) if OPENCODE_PASSWORD else None
    
    try:
        response = requests.post(
            f"{OPENCODE_SERVER}/session/{session}/message",
            json={"agent": "greenbriar", "parts": [{"type": "text", "text": message}]},
            auth=auth,
            timeout=300  # 5分钟超时
        )
    except requests.exceptions.Timeout:
        return "请求超时，AI 处理时间过长，请稍后重试"
    except requests.exceptions.ConnectionError:
        return "无法连接到 OpenCode Server，请确认服务已启动"
    
    if response.status_code == 200:
        if not response.text.strip():
            return "OpenCode 返回了空响应"
        result = response.json()
        parts = result.get("parts", [])
        return "\n".join([p.get("text", "") for p in parts if p.get("type") == "text"])
    return f"错误: {response.status_code} - {response.text[:200]}"

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return
    await update.message.reply_text("处理中...")
    response = send_message_to_opencode("你好")
    await update.message.reply_text(response[:4000])

async def reset_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global session_id
    if not update.message:
        return
    session_id = None
    await update.message.reply_text("会话已重置")

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return
    await update.message.reply_text(
        f"服务器: {OPENCODE_SERVER}\n"
        f"会话ID: {session_id or '未创建'}"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
    user_message = update.message.text

    await update.message.reply_text("处理中...")

    response = send_message_to_opencode(user_message)

    await update.message.reply_text(response[:4000])

def main():
    if not TELEGRAM_BOT_TOKEN:
        print("请设置 TELEGRAM_BOT_TOKEN 环境变量")
        return
    
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("reset", reset_command))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    if WEBHOOK_URL:
        application.run_webhook(
            listen="0.0.0.0",
            port=int(os.getenv("PORT", "8443")),
            url_path="webhook",
            webhook_url=WEBHOOK_URL,
            allowed_updates=Update.ALL_TYPES
        )
        logger.info(f"Webhook 模式已启动: {WEBHOOK_URL}")
    else:
        application.run_polling(allowed_updates=Update.ALL_TYPES)
        logger.info("Polling 模式已启动")

if __name__ == "__main__":
    main()
