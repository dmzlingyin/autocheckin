"""
通知模块
支持多种通知方式：Server酱、PushPlus等
"""

import requests
import os
import logging
from typing import List, Dict, Any, Optional
from base_checkin import CheckinResult
from config import get_config_manager

logger = logging.getLogger(__name__)


class NotifyResult:
    """通知结果类"""
    
    def __init__(self, success: bool, message: str, platform: str):
        self.success = success
        self.message = message
        self.platform = platform
    
    def __str__(self):
        return f"NotifyResult(success={self.success}, platform='{self.platform}', message='{self.message}')"


class BaseNotifier:
    """通知基础类"""
    
    def __init__(self, name: str):
        self.name = name
        self.logger = logging.getLogger(f"{__name__}.{name}")
    
    def send(self, title: str, content: str, **kwargs) -> NotifyResult:
        """
        发送通知
        
        Args:
            title: 通知标题
            content: 通知内容
            **kwargs: 其他参数
            
        Returns:
            NotifyResult: 通知结果
        """
        raise NotImplementedError


class ServerChanNotifier(BaseNotifier):
    """Server酱通知"""
    
    def __init__(self, sckey: str):
        super().__init__("Server酱")
        self.sckey = sckey
        self.api_url = "https://sctapi.ftqq.com"
    
    def send(self, title: str, content: str, **kwargs) -> NotifyResult:
        try:
            if not self.sckey:
                return NotifyResult(False, "未配置Server酱密钥", self.name)
            
            url = f"{self.api_url}/{self.sckey}.send"
            data = {
                'title': title,
                'desp': content
            }
            
            response = requests.post(url, data=data, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            if result.get('code') == 0:
                return NotifyResult(True, "发送成功", self.name)
            else:
                return NotifyResult(False, f"发送失败: {result.get('message', '未知错误')}", self.name)
                
        except Exception as e:
            self.logger.error(f"Server酱通知发送失败: {e}")
            return NotifyResult(False, f"发送异常: {str(e)}", self.name)


class PushPlusNotifier(BaseNotifier):
    """PushPlus通知"""
    
    def __init__(self, token: str):
        super().__init__("PushPlus")
        self.token = token
        self.api_url = "http://www.pushplus.plus/send"
    
    def send(self, title: str, content: str, **kwargs) -> NotifyResult:
        try:
            if not self.token:
                return NotifyResult(False, "未配置PushPlus令牌", self.name)
            
            data = {
                'token': self.token,
                'title': title,
                'content': content,
                'template': 'html'
            }
            
            response = requests.get(self.api_url, params=data, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            if result.get('code') == 200:
                return NotifyResult(True, "发送成功", self.name)
            else:
                return NotifyResult(False, f"发送失败: {result.get('msg', '未知错误')}", self.name)
                
        except Exception as e:
            self.logger.error(f"PushPlus通知发送失败: {e}")
            return NotifyResult(False, f"发送异常: {str(e)}", self.name)


class NotifyManager:
    """通知管理器"""
    
    def __init__(self):
        self.notifiers: List[BaseNotifier] = []
        self.logger = logging.getLogger(__name__)
    
    def add_notifier(self, notifier: BaseNotifier):
        """添加通知器"""
        self.notifiers.append(notifier)
    
    def send_all(self, title: str, content: str, **kwargs) -> List[NotifyResult]:
        """
        发送通知到所有配置的通知器
        
        Args:
            title: 通知标题
            content: 通知内容
            **kwargs: 其他参数
            
        Returns:
            List[NotifyResult]: 所有通知结果
        """
        results = []
        for notifier in self.notifiers:
            result = notifier.send(title, content, **kwargs)
            results.append(result)
            self.logger.info(f"{notifier.name} 通知结果: {result}")
        return results
    
    def send_checkin_results(self, results: List[CheckinResult], **kwargs) -> List[NotifyResult]:
        """
        发送签到结果通知
        
        Args:
            results: 签到结果列表
            **kwargs: 其他参数
            
        Returns:
            List[NotifyResult]: 通知结果
        """
        if not results:
            return []
        
        # 统计签到结果
        success_count = sum(1 for r in results if r.success)
        total_count = len(results)
        
        # 生成通知内容
        title = f"自动签到报告 ({success_count}/{total_count})"
        
        content_lines = [f"签到时间: {results[0].data.get('timestamp', '未知')}"]
        content_lines.append(f"成功: {success_count}/{total_count}")
        content_lines.append("")
        
        for result in results:
            status = "✅" if result.success else "❌"
            content_lines.append(f"{status} {result.data.get('site_name', '未知站点')}: {result.message}")
        
        content = "\n".join(content_lines)
        
        return self.send_all(title, content, **kwargs)


def create_notify_manager() -> NotifyManager:
    """
    创建通知管理器并配置通知器
    
    Returns:
        NotifyManager: 配置好的通知管理器
    """
    manager = NotifyManager()
    
    # 使用配置管理器获取通知配置
    config_manager = get_config_manager()
    notify_config = config_manager.get_notify_config()
    
    if notify_config:
        # 配置Server酱
        server_chan_config = notify_config.get('server_chan', {})
        if server_chan_config.get('sckey'):
            manager.add_notifier(ServerChanNotifier(server_chan_config['sckey']))
        
        # 配置PushPlus
        pushplus_config = notify_config.get('pushplus', {})
        if pushplus_config.get('token'):
            manager.add_notifier(PushPlusNotifier(pushplus_config['token']))
        
        # 配置其他通知方式
        # 可以在这里添加更多通知方式的配置
    else:
        logger.warning("未配置通知服务")
    
    return manager 