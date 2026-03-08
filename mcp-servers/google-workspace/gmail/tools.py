"""
Gmail MCP 工具定义
"""
import logging
import json
from typing import Optional
from mcp.server.fastmcp import FastMCP

try:
    from .gmail_client import GmailClient
    from common.oauth import authenticate
except ImportError:
    import sys
    from pathlib import Path

    sys.path.append(str(Path(__file__).resolve().parents[1]))
    from gmail_client import GmailClient
    from common.oauth import authenticate

logger = logging.getLogger(__name__)

# 初始化 MCP 服务器
mcp = FastMCP("gmail")

# 全局变量存储客户端
gmail_client: Optional[GmailClient] = None


def ensure_gmail_client():
    """确保 Gmail 客户端已初始化"""
    global gmail_client
    if gmail_client is None:
        credentials = authenticate()
        if credentials:
            gmail_client = GmailClient(credentials)
        else:
            raise RuntimeError("无法获取 Gmail 凭证")


@mcp.tool()
async def gmail_get_messages(
    max_results: int = 10,
    query: str = "is:inbox"
) -> str:
    """
    获取收件箱的邮件列表
    
    Args:
        max_results: 最多返回多少封邮件
        query: Gmail 查询语法（如 is:unread, from:xxx）
    
    Returns:
        邮件列表的 JSON 字符串
    """
    try:
        ensure_gmail_client()
        assert gmail_client is not None
        
        result = gmail_client.get_messages(query=query, max_results=max_results)
        
        # 格式化输出
        messages = result.get('messages', [])
        output = []
        
        for msg in messages:
            msg_id = msg.get('id', '')
            snippet = msg.get('snippet', '')
            output.append({
                'id': msg_id,
                'snippet': snippet
            })
        
        logger.info(f"返回 {len(output)} 封邮件")
        return json.dumps(output, ensure_ascii=False)
    
    except Exception as e:
        logger.error(f"获取邮件失败: {e}")
        return f"错误: {str(e)}"


@mcp.tool()
async def gmail_get_message(
    message_id: str
) -> str:
    """
    获取单封邮件的详细内容
    
    Args:
        message_id: 邮件 ID
    
    Returns:
        邮件详细内容的 JSON 字符串
    """
    try:
        ensure_gmail_client()
        assert gmail_client is not None
        
        message = gmail_client.get_message(message_id=message_id)
        logger.info(f"获取邮件详情: {message_id}")
        
        return json.dumps(message, ensure_ascii=False)
    
    except Exception as e:
        logger.error(f"获取邮件详情失败: {e}")
        return f"错误: {str(e)}"


@mcp.tool()
async def gmail_search_messages(
    query: str,
    max_results: int = 10
) -> str:
    """
    搜索特定邮件
    
    Args:
        query: 搜索查询（Gmail 查询语法）
        max_results: 最多返回结果数
    
    Returns:
        搜索结果的 JSON 字符串
    """
    try:
        ensure_gmail_client()
        assert gmail_client is not None
        
        result = gmail_client.search_messages(query=query, max_results=max_results)
        
        logger.info(f"搜索邮件，查询: {query}")
        return json.dumps(result, ensure_ascii=False)
    
    except Exception as e:
        logger.error(f"搜索邮件失败: {e}")
        return f"错误: {str(e)}"


@mcp.tool()
async def gmail_create_draft(
    to: str,
    subject: str,
    body: str
) -> str:
    """
    在草稿箱创建邮件
    
    Args:
        to: 收件人邮箱
        subject: 邮件主题
        body: 邮件正文
    
    Returns:
        创建结果的 JSON 字符串
    """
    try:
        ensure_gmail_client()
        assert gmail_client is not None
        
        draft = gmail_client.create_draft(to=to, subject=subject, body=body)
        
        logger.info(f"创建草稿: {subject}")
        return json.dumps(draft, ensure_ascii=False)
    
    except Exception as e:
        logger.error(f"创建草稿失败: {e}")
        return f"错误: {str(e)}"


@mcp.tool()
async def gmail_mark_read(
    message_id: str
) -> str:
    """
    标记邮件为已读
    
    Args:
        message_id: 邮件 ID
    
    Returns:
        操作结果的 JSON 字符串
    """
    try:
        ensure_gmail_client()
        assert gmail_client is not None
        
        result = gmail_client.mark_read(message_id=message_id)
        
        logger.info(f"标记邮件已读: {message_id}")
        return json.dumps(result, ensure_ascii=False)
    
    except Exception as e:
        logger.error(f"标记已读失败: {e}")
        return f"错误: {str(e)}"


def main():
    """启动 Gmail MCP 服务器"""
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    logger.info("Gmail MCP 服务器启动")
    
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
