"""OAuth 2.0 认证管理模块。"""

import logging
import os
import sys

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

from .config import Config
from .token_store import TokenStore

logger = logging.getLogger(__name__)


class OAuthManager:
    """OAuth 2.0 认证管理器。"""

    def __init__(self) -> None:
        self.token_store = TokenStore()

    @staticmethod
    def _client_config() -> dict:
        Config.validate_oauth_config()
        return {
            "installed": {
                "client_id": Config.GOOGLE_CLIENT_ID,
                "client_secret": Config.GOOGLE_CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [Config.GOOGLE_REDIRECT_URI],
            }
        }

    def _run_local_oauth(self):
        if Config.GOOGLE_REDIRECT_URI.startswith("http://localhost") or Config.GOOGLE_REDIRECT_URI.startswith("http://127.0.0.1"):
            os.environ.setdefault("OAUTHLIB_INSECURE_TRANSPORT", "1")

        scopes = Config.GMAIL_SCOPES + Config.CALENDAR_SCOPES
        flow = InstalledAppFlow.from_client_config(self._client_config(), scopes=scopes)
        creds = flow.run_local_server(
            host="127.0.0.1",
            port=8080,
            open_browser=True,
            authorization_prompt_message="请在浏览器完成 Google 授权...",
            success_message="认证成功，可以关闭此窗口。",
            timeout_seconds=300,
        )
        self.token_store.save_token(creds)
        return creds

    def _run_manual_oauth(self):
        """不启动本地回调服务，手动粘贴授权回跳 URL。"""
        if Config.GOOGLE_REDIRECT_URI.startswith("http://localhost") or Config.GOOGLE_REDIRECT_URI.startswith("http://127.0.0.1"):
            os.environ.setdefault("OAUTHLIB_INSECURE_TRANSPORT", "1")

        scopes = Config.GMAIL_SCOPES + Config.CALENDAR_SCOPES
        flow = InstalledAppFlow.from_client_config(
            self._client_config(),
            scopes=scopes,
            redirect_uri=Config.GOOGLE_REDIRECT_URI,
        )

        auth_url, _ = flow.authorization_url(
            access_type="offline",
            prompt="consent",
            include_granted_scopes="true",
        )

        print("\n=== Google OAuth 手动授权模式 ===")
        print("1) 在浏览器打开下面链接并完成授权")
        print(auth_url)
        print("2) 授权完成后，即使页面显示无法访问，也没关系")
        print("3) 复制浏览器地址栏完整 URL，粘贴到这里\n")

        if not sys.stdin.isatty():
            raise RuntimeError("当前为非交互环境，manual 模式无法读取粘贴输入")

        redirected_url = input("请粘贴完整回跳 URL: ").strip()
        if not redirected_url:
            raise RuntimeError("未输入回跳 URL")

        flow.fetch_token(authorization_response=redirected_url)
        creds = flow.credentials
        self.token_store.save_token(creds)
        return creds

    def get_credentials(self):
        creds = self.token_store.load_token()
        if creds and creds.valid:
            return creds

        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                self.token_store.save_token(creds)
                return creds
            except Exception as exc:
                logger.warning("刷新凭证失败，将重新授权: %s", exc)

        logger.info("未找到有效凭证，启动 OAuth 授权流程")
        if Config.OAUTH_MODE.lower() == "local":
            return self._run_local_oauth()
        return self._run_manual_oauth()


def authenticate():
    """认证并返回 Google Credentials。"""
    return OAuthManager().get_credentials()
