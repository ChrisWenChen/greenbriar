"""
配置管理模块
"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class Config:
    """配置管理类"""
    
    # OAuth 配置
    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
    GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
    GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8080/")
    OAUTH_MODE = os.getenv("OAUTH_MODE", "manual")
    
    # OAuth Scopes
    GMAIL_SCOPES = [
        "https://www.googleapis.com/auth/gmail.readonly",
        "https://www.googleapis.com/auth/gmail.compose",
        "https://www.googleapis.com/auth/gmail.modify",
    ]
    
    CALENDAR_SCOPES = [
        "https://www.googleapis.com/auth/calendar",
        "https://www.googleapis.com/auth/calendar.events",
        "https://www.googleapis.com/auth/calendar.readonly"
    ]
    
    # Token 存储路径
    TOKEN_DIR = Path.home() / ".greenbriar"
    TOKEN_FILE = TOKEN_DIR / "google_workspace_token.json"
    
    # 日志配置
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    @classmethod
    def validate_oauth_config(cls) -> bool:
        """验证 OAuth 配置是否完整"""
        if not cls.GOOGLE_CLIENT_ID:
            raise ValueError("GOOGLE_CLIENT_ID 环境变量未设置")
        if not cls.GOOGLE_CLIENT_SECRET:
            raise ValueError("GOOGLE_CLIENT_SECRET 环境变量未设置")
        return True
    
    @classmethod
    def ensure_token_dir(cls) -> Path:
        """确保 Token 目录存在"""
        cls.TOKEN_DIR.mkdir(parents=True, exist_ok=True)
        return cls.TOKEN_FILE
