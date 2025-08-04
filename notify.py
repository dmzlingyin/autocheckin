"""
通知模块
支持Server酱等通知服务
"""

import requests
import logging
from typing import List, Dict, Any
from collections import defaultdict
from config import get_notify_config

logger = logging.getLogger(__name__)


def send_notification(results: List[Dict[str, Any]]):
    """
    发送签到结果通知
    
    Args:
        results: 签到结果列表
    """
    if not results:
        logger.info("没有签到结果，跳过通知")
        return
    
    # 获取通知配置
    notify_config = get_notify_config()
    if not notify_config:
        logger.info("未配置通知服务，跳过通知")
        return
    
    # 统计结果
    success_count = sum(1 for r in results if r['success'])
    total_count = len(results)
    
    # 构建通知内容
    title = f"🎯 自动签到报告 ({success_count}/{total_count})"
    content = build_notification_content(results)
    
    # 发送通知
    send_server_chan(title, content, notify_config)


def build_notification_content(results: List[Dict[str, Any]]) -> str:
    """构建分等级、分平台、分账号的通知内容"""
    if not results:
        return "❌ 没有签到结果"
    
    # 统计结果
    success_count = sum(1 for r in results if r['success'])
    total_count = len(results)
    
    # 构建头部
    content_lines = []
    content_lines.append("🚀 **自动签到完成**")
    content_lines.append("")
    
    # 添加等级总结
    if success_count == total_count:
        content_lines.append("🎉 **全部成功** - 太棒了！")
    elif success_count > 0:
        content_lines.append(f"⚠️ **部分成功** - {success_count}/{total_count}")
    else:
        content_lines.append("💥 **全部失败** - 需要检查配置")
    
    content_lines.append("")
    content_lines.append("---")
    content_lines.append("")
    
    # 分平台分账号输出
    grouped = defaultdict(list)
    for r in results:
        platform = r.get('platform', '未知平台')
        grouped[platform].append(r)
    
    for platform, items in grouped.items():
        content_lines.append(f"### 🏷️ 平台：{platform}")
        for i, result in enumerate(items, 1):
            if result['success']:
                status_icon = "✅"
                status_text = "成功"
            else:
                status_icon = "❌"
                status_text = "失败"
            content_lines.append(f"- **账号 {i}：{result['account']}**  {status_icon} {status_text}")
            content_lines.append(f"    - 💬 {result['message']}")
        content_lines.append("")
    
    # 添加底部信息
    content_lines.append("---")
    content_lines.append("")
    content_lines.append("⏰ 签到时间: " + get_current_time())
    content_lines.append("🤖 由自动签到机器人发送")
    
    return "\n".join(content_lines)


def get_current_time() -> str:
    """获取当前时间"""
    from datetime import datetime
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def send_server_chan(title: str, content: str, config: Dict[str, Any]):
    """发送Server酱通知"""
    sckey = config.get('key')
    if not sckey:
        return
    
    try:
        url = f"https://sctapi.ftqq.com/{sckey}.send"
        data = {
            'title': title,
            'desp': content
        }
        
        response = requests.post(url, data=data, timeout=10)
        response.raise_for_status()
        
        result = response.json()
        if result.get('code') == 0:
            logger.info("Server酱通知发送成功")
        else:
            logger.warning(f"Server酱通知发送失败: {result.get('message', '未知错误')}")
            
    except Exception as e:
        logger.error(f"Server酱通知发送异常: {e}")
