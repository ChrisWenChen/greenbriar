"""Google OAuth 授权初始化脚本，供 setup.sh 调用。"""

import sys
from pathlib import Path
from dotenv import load_dotenv

# 加载 .env（相对于本脚本所在目录）
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)

# 确保 stdin 连接到终端（setup.sh 可能通过管道调用，导致 isatty() 返回 False）
if not sys.stdin.isatty():
    try:
        sys.stdin = open("/dev/tty", "r")
    except OSError:
        pass  # 无法打开 /dev/tty 时交给 oauth.py 自行报错

from common.oauth import authenticate

try:
    creds = authenticate()
    print("[OK] 授权成功！")
except Exception as e:
    print(f"[ERR] 授权失败: {e}")
    sys.exit(1)
