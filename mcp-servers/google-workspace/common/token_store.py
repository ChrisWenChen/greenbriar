"""Token 持久化管理模块。"""

import json
import logging
from pathlib import Path

from google.oauth2.credentials import Credentials

from .config import Config

logger = logging.getLogger(__name__)


class TokenStore:
    """Google OAuth Token 文件存储。"""

    def __init__(self, token_path: str | None = None) -> None:
        self.token_path = Path(token_path) if token_path else Config.ensure_token_dir()

    def load_token(self):
        if not self.token_path.exists():
            return None
        try:
            data = json.loads(self.token_path.read_text(encoding="utf-8"))
            return Credentials.from_authorized_user_info(data)
        except Exception as exc:
            logger.warning("读取 token 失败: %s", exc)
            return None

    def save_token(self, credentials) -> None:
        self.token_path.parent.mkdir(parents=True, exist_ok=True)
        payload = credentials.to_json()
        self.token_path.write_text(payload, encoding="utf-8")

    def delete_token(self) -> None:
        if self.token_path.exists():
            self.token_path.unlink()
