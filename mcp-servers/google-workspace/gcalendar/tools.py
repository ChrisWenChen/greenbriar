"""
Calendar MCP 工具定义
"""
import logging
import json
from typing import Optional
from mcp.server.fastmcp import FastMCP

try:
    from .calendar_client import CalendarClient
    from common.oauth import authenticate
except ImportError:
    import sys
    from pathlib import Path

    sys.path.append(str(Path(__file__).resolve().parents[1]))
    from calendar_client import CalendarClient
    from common.oauth import authenticate

logger = logging.getLogger(__name__)

# 初始化 MCP 服务器
mcp = FastMCP("calendar")

# 全局变量存储客户端
calendar_client: Optional[CalendarClient] = None


def ensure_calendar_client():
    """确保 Calendar 客户端已初始化"""
    global calendar_client
    if calendar_client is None:
        credentials = authenticate()
        if credentials:
            calendar_client = CalendarClient(credentials)
        else:
            raise RuntimeError("无法获取 Calendar 凭证")


def format_rfc3339_datetime(dt_string: str) -> str:
    """
    格式化日期时间为 RFC3339 格式
    
    Args:
        dt_string: 日期时间字符串
        
    Returns:
        RFC3339 格式字符串
    """
    try:
        # 接受 ISO 格式，直接原样用于 Google API
        return dt_string
    except Exception:
        return dt_string


@mcp.tool()
async def calendar_list_calendars() -> str:
    """
    列出所有日历
    
    Returns:
        日历列表的 JSON 字符串
    """
    try:
        ensure_calendar_client()
        assert calendar_client is not None
        
        calendars = calendar_client.list_calendars()
        
        # 格式化输出
        output = []
        for cal in calendars:
            cal_id = cal.get('id', '')
            name = cal.get('summary', '无标题')
            output.append({
                'id': cal_id,
                'name': name
            })
        
        logger.info(f"返回 {len(output)} 个日历")
        return json.dumps(output, ensure_ascii=False)
    
    except Exception as e:
        logger.error(f"获取日历列表失败: {e}")
        return f"错误: {str(e)}"


@mcp.tool()
async def calendar_list_events(
    calendar_id: str = "primary",
    time_min: str | None = None,
    time_max: str | None = None,
    max_results: int = 10
) -> str:
    """
    列出事件
    
    Args:
        calendar_id: 日历 ID，默认 'primary'
        time_min: 开始时间（RFC3339 格式）
        time_max: 结束时间（RFC3339 格式）
        max_results: 最多返回结果多少
    
    Returns:
        事件列表的 JSON 字符串
    """
    try:
        ensure_calendar_client()
        assert calendar_client is not None
        
        # 格式化时间
        formatted_time_min = format_rfc3339_datetime(time_min) if time_min else None
        formatted_time_max = format_rfc3339_datetime(time_max) if time_max else None
        
        events = calendar_client.list_events(
            calendar_id=calendar_id,
            time_min=formatted_time_min,
            time_max=formatted_time_max,
            max_results=max_results
        )
        
        # 格式化输出
        output = []
        for event in events:
            evt_id = event.get('id', '')
            summary = event.get('summary', '无标题')
            start = event.get('start', {}).get('dateTime', '')
            output.append({
                'id': evt_id,
                'summary': summary,
                'start': start
            })
        
        logger.info(f"返回 {len(output)} 个事件")
        return json.dumps(output, ensure_ascii=False)
    
    except Exception as e:
        logger.error(f"获取事件列表失败: {e}")
        return f"错误: {str(e)}"


@mcp.tool()
async def calendar_get_event(
    event_id: str,
    calendar_id: str = "primary"
) -> str:
    """
    获取事件详情
    
    Args:
        event_id: 事件 ID
        calendar_id: 日历 ID，默认 'primary'
    
    Returns:
        事件详情的 JSON 字符串
    """
    try:
        ensure_calendar_client()
        assert calendar_client is not None
        
        event = calendar_client.get_event(calendar_id=calendar_id, event_id=event_id)
        logger.info(f"获取事件详情: {event_id}")
        
        return json.dumps(event, ensure_ascii=False)
    
    except Exception as e:
        logger.error(f"获取事件详情失败: {e}")
        return f"错误: {str(e)}"


@mcp.tool()
async def calendar_search_events(
    query: str,
    calendar_id: str = "primary",
    max_results: int = 10
) -> str:
    """
    搜索事件
    
    Args:
        query: 搜索关键词
        calendar_id: 日历 ID，默认 'primary'
        max_results: 最多返回结果数
    
    Returns:
        搜索结果的 JSON 字符串
    """
    try:
        ensure_calendar_client()
        assert calendar_client is not None
        
        events = calendar_client.search_events(
            query=query,
            calendar_id=calendar_id,
            max_results=max_results
        )
        
        logger.info(f"搜索事件，查询: {query}")
        return json.dumps(events, ensure_ascii=False)
    
    except Exception as e:
        logger.error(f"搜索事件失败: {e}")
        return f"错误: {str(e)}"


@mcp.tool()
async def calendar_create_event(
    summary: str,
    start_time: str,
    end_time: str,
    calendar_id: str = "primary",
    description: str = "",
    attendees: list | None = None,
    color_id: str | None = None,
) -> str:
    """
    在日历上创建新事件
    
    Args:
        calendar_id: 日历 ID（default 表示主日历）
        summary: 事件标题
        start_time: 开始时间（RFC3339 格式或 ISO 格式）
        end_time: 结束时间（RFC3339 格式或 ISO 格式）
        description: 事件描述
        attendees: 参会者邮箱列表
        color_id: 事件颜色 ID，可选值："1"(Lavender), "2"(Sage), "3"(Grape), "4"(Flamingo), "5"(Banana), "6"(Tangerine), "7"(Peacock), "8"(Graphite), "9"(Blueberry), "10"(Basil), "11"(Tomato)
    
    Returns:
        创建事件的 JSON 字符串
    """
    try:
        ensure_calendar_client()
        assert calendar_client is not None
        
        # 格式化时间
        formatted_start_time = format_rfc3339_datetime(start_time)
        formatted_end_time = format_rfc3339_datetime(end_time)
        
        event = calendar_client.create_event(
            calendar_id=calendar_id,
            summary=summary,
            start_time=formatted_start_time,
            end_time=formatted_end_time,
            description=description,
            attendees=attendees,
            color_id=color_id
        )
        
        logger.info(f"创建事件成功: {summary}")
        return json.dumps(event, ensure_ascii=False)
    
    except Exception as e:
        logger.error(f"创建事件失败: {e}")
        return f"错误: {str(e)}"


@mcp.tool()
async def calendar_update_event(
    event_id: str,
    calendar_id: str = "primary",
    summary: str | None = None,
    start_time: str | None = None,
    end_time: str | None = None,
    description: str | None = None,
    color_id: str | None = None,
) -> str:
    """
    更新已有事件
    
    Args:
        event_id: 事件 ID
        calendar_id: 日历 ID，默认 'primary'
        summary: 事件标题（可选）
        start_time: 开始时间（可选）
        end_time: 结束时间（可选）
        description: 事件描述（可选）
        color_id: 事件颜色 ID（可选），可选值："1"(Lavender), "2"(Sage), "3"(Grape), "4"(Flamingo), "5"(Banana), "6"(Tangerine), "7"(Peacock), "8"(Graphite), "9"(Blueberry), "10"(Basil), "11"(Tomato)
    
    Returns:
        更新后的事件 JSON 字符串
    """
    try:
        ensure_calendar_client()
        assert calendar_client is not None
        
        # 格式化时间
        formatted_start_time = format_rfc3339_datetime(start_time) if start_time else None
        formatted_end_time = format_rfc3339_datetime(end_time) if end_time else None
        
        event = calendar_client.update_event(
            calendar_id=calendar_id,
            event_id=event_id,
            summary=summary,
            start_time=formatted_start_time,
            end_time=formatted_end_time,
            description=description,
            color_id=color_id
        )
        
        logger.info(f"更新事件成功: {event_id}")
        return json.dumps(event, ensure_ascii=False)
    
    except Exception as e:
        logger.error(f"更新事件失败: {e}")
        return f"错误: {str(e)}"


@mcp.tool()
async def calendar_delete_event(
    event_id: str,
    calendar_id: str = "primary"
) -> str:
    """
    删除事件
    
    Args:
        event_id: 事件 ID
        calendar_id: 日历 ID，默认 'primary'
    
    Returns:
        删除结果的 JSON 字符串
    """
    try:
        ensure_calendar_client()
        assert calendar_client is not None
        
        result = calendar_client.delete_event(calendar_id=calendar_id, event_id=event_id)
        
        logger.info(f"删除事件成功: {event_id}")
        return json.dumps(result, ensure_ascii=False)
    
    except Exception as e:
        logger.error(f"删除事件失败: {e}")
        return f"错误: {str(e)}"


@mcp.tool()
async def calendar_check_freebusy(
    time_min: str,
    time_max: str,
    calendar_ids: list | None = None,
) -> str:
    """
    检查某段时间是否空闲
    
    Args:
        time_min: 开始时间（RFC3339 格式）
        time_max: 结束时间（RFC3339 格式）
        calendar_ids: 日历 ID 列表，默认 ["primary"]
    
    Returns:
        忙闲状态信息的 JSON 字符串
    """
    try:
        ensure_calendar_client()
        assert calendar_client is not None
        
        # 格式化时间
        formatted_time_min = format_rfc3339_datetime(time_min)
        formatted_time_max = format_rfc3339_datetime(time_max)
        target_calendar_ids = calendar_ids or ["primary"]
        
        freebusy = calendar_client.check_freebusy(
            calendar_ids=target_calendar_ids,
            time_min=formatted_time_min,
            time_max=formatted_time_max
        )
        
        logger.info("查询忙闲状态成功")
        return json.dumps(freebusy, ensure_ascii=False)
    
    except Exception as e:
        logger.error(f"查询忙闲失败: {e}")
        return f"错误: {str(e)}"


@mcp.tool()
async def calendar_get_current_time() -> str:
    """
    获取当前日期和时间
    
    Returns:
        当前时间信息的 JSON 字符串
    """
    try:
        ensure_calendar_client()
        assert calendar_client is not None
        
        time_info = calendar_client.get_current_time()
        logger.info("获取当前时间成功")
        
        return json.dumps(time_info, ensure_ascii=False)
    
    except Exception as e:
        logger.error(f"获取当前时间失败: {e}")
        return f"错误: {str(e)}"


def main():
    """启动 Calendar MCP 服务器"""
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    logger.info("Calendar MCP 服务器启动")
    
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
