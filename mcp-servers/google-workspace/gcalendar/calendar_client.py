"""
Calendar API 客户端模块
"""
import logging
from datetime import datetime, timezone

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
logger = logging.getLogger(__name__)

class CalendarClient:
    """Calendar API 客户端封装类"""
    
    def __init__(self, credentials):
        """
        初始化 Calendar API 客户端
        
        Args:
            credentials: OAuth 2.0 凭证对象
        """
        try:
            self.service = build('calendar', 'v3', credentials=credentials)
            logger.info("Calendar API 客户端初始化成功")
        except Exception as e:
            logger.error(f"Calendar API 客户端初始化失败: {e}")
            raise
    
    def list_calendars(self):
        """
        列出所有日历
        
        Returns:
            日历列表
        """
        try:
            calendar_list = self.service.calendarList().list().execute()
            calendars = calendar_list.get('items', [])
            logger.info(f"获取到 {len(calendars)} 个日历")
            return calendars
        except HttpError as e:
            logger.error(f"获取日历列表失败: {e}")
            raise
        except Exception as e:
            logger.error(f"未知错误: {e}")
            raise
    
    def list_events(self, calendar_id='primary', time_min=None, time_max=None, max_results=10):
        """
        列出事件
        
        Args:
            calendar_id: 日历 ID，默认 'primary'
            time_min: 开始时间（RFC3339）
            time_max: 结束时间（RFC3339）
            max_results: 最多返回结果数
        
        Returns:
            事件列表
        """
        try:
            events_result = self.service.events().list(
                calendarId=calendar_id,
                timeMin=time_min,
                timeMax=time_max,
                maxResults=max_results
            ).execute()
            
            events = events_result.get('items', [])
            logger.info(f"获取到 {len(events)} 个事件")
            return events
        except HttpError as e:
            logger.error(f"获取事件列表失败: {e}")
            raise
        except Exception as e:
            logger.error(f"未知错误: {e}")
            raise
    
    def get_event(self, calendar_id='primary', event_id=None):
        """
        获取事件详情
        
        Args:
            calendar_id: 日历 ID
            event_id: 事件 ID
        
        Returns:
            事件详情
        """
        try:
            event = self.service.events().get(
                calendarId=calendar_id,
                eventId=event_id
            ).execute()
            
            logger.info(f"获取事件详情: {event_id}")
            return event
        except HttpError as e:
            logger.error(f"获取事件详情失败: {e}")
            raise
        except Exception as e:
            logger.error(f"未知错误: {e}")
            raise
    
    def search_events(self, query, calendar_id='primary', max_results=10):
        """
        搜索事件
        
        Args:
            query: 搜索关键词
            calendar_id: 日历 ID
            max_results: 最多返回结果数
        
        Returns:
            搜索结果
        """
        try:
            # 使用 Gmail 风格的搜索
            events_result = self.service.events().list(
                calendarId=calendar_id,
                q=query,
                maxResults=max_results
            ).execute()
            
            events = events_result.get('items', [])
            logger.info(f"搜索到 {len(events)} 个事件")
            return events
        except HttpError as e:
            logger.error(f"搜索事件失败: {e}")
            raise
        except Exception as e:
            logger.error(f"未知错误: {e}")
            raise
    
    def create_event(self, calendar_id='primary', summary='', start_time=None, end_time=None, description='', attendees=None, color_id=None):
        """
        创建事件
        
        Args:
            calendar_id: 日历 ID
            summary: 事件标题
            start_time: 开始时间（RFC3339）
            end_time: 结束时间（RFC3339）
            description: 事件描述
            attendees: 参会者列表
            color_id: 事件颜色 ID（"1"-"11"）
        
        Returns:
            创建的事件
        """
        try:
            event = {
                'summary': summary,
                'start': {
                    'dateTime': start_time
                },
                'end': {
                    'dateTime': end_time
                },
                'description': description
            }
            
            if attendees:
                event['attendees'] = [{'email': email} for email in attendees]
            
            if color_id:
                event['colorId'] = str(color_id)
            
            created_event = self.service.events().insert(
                calendarId=calendar_id,
                body=event
            ).execute()
            
            logger.info(f"创建事件成功: {summary}")
            return created_event
        except HttpError as e:
            logger.error(f"创建事件失败: {e}")
            raise
        except Exception as e:
            logger.error(f"未知错误: {e}")
            raise
    
    def update_event(self, calendar_id='primary', event_id=None, summary=None, start_time=None, end_time=None, description=None, color_id=None):
        """
        更新事件
        
        Args:
            calendar_id: 日历 ID
            event_id: 事件 ID
            summary: 事件标题（可选）
            start_time: 开始时间（可选）
            end_time: 结束时间（可选）
            description: 事件描述（可选）
            color_id: 事件颜色 ID（"1"-"11"，可选）
        
        Returns:
            更新后的事件
        """
        try:
            # 先获取现有事件
            event = self.service.events().get(
                calendarId=calendar_id,
                eventId=event_id
            ).execute()
            
            # 更新字段
            if summary is not None:
                event['summary'] = summary
            if start_time is not None:
                event['start'] = {'dateTime': start_time}
            if end_time is not None:
                event['end'] = {'dateTime': end_time}
            if description is not None:
                event['description'] = description
            if color_id is not None:
                event['colorId'] = str(color_id)
            
            # 提交更新
            updated_event = self.service.events().update(
                calendarId=calendar_id,
                eventId=event_id,
                body=event
            ).execute()
            
            logger.info(f"更新事件成功: {event_id}")
            return updated_event
        except HttpError as e:
            logger.error(f"更新事件失败: {e}")
            raise
        except Exception as e:
            logger.error(f"未知错误: {e}")
            raise
    
    def delete_event(self, calendar_id='primary', event_id=None):
        """
        删除事件
        
        Args:
            calendar_id: 日历 ID
            event_id: 事件 ID
        
        Returns:
            删除结果
        """
        try:
            result = self.service.events().delete(
                calendarId=calendar_id,
                eventId=event_id
            ).execute()
            
            logger.info(f"删除事件成功: {event_id}")
            return result
        except HttpError as e:
            logger.error(f"删除事件失败: {e}")
            raise
        except Exception as e:
            logger.error(f"未知错误: {e}")
            raise
    
    def check_freebusy(self, calendar_ids=None, time_min=None, time_max=None):
        """
        检查忙闲
        
        Args:
            calendar_ids: 日历 ID 列表
            time_min: 开始时间
            time_max: 结束时间
        
        Returns:
            忙闲状态信息
        """
        try:
            target_calendar_ids = calendar_ids or ['primary']
            freebusy_request = {
                'timeMin': time_min,
                'timeMax': time_max,
                'items': [{'id': cal_id} for cal_id in target_calendar_ids]
            }
            
            freebusy_result = self.service.freebusy().query(body=freebusy_request).execute()
            
            logger.info("查询忙闲状态成功")
            return freebusy_result
        except HttpError as e:
            logger.error(f"查询忙闲失败: {e}")
            raise
        except Exception as e:
            logger.error(f"未知错误: {e}")
            raise
    
    def get_current_time(self):
        """
        获取当前时间
        
        Returns:
            当前时间信息
        """
        try:
            current_time = datetime.now(timezone.utc)
            
            logger.info("获取当前时间成功")
            return {
                'datetime': current_time.isoformat(),
                'timezone': 'UTC',
                'isoformat': current_time.isoformat()
            }
        except Exception as e:
            logger.error(f"获取当前时间失败: {e}")
            raise
