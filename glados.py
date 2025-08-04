"""
GLaDOS 签到模块
"""

import requests
import logging
from typing import Dict, Any, List
from base_checkin import BaseCheckin
from config import get_glados_config

logger = logging.getLogger(__name__)


class GLaDOSCheckin(BaseCheckin):
    """GLaDOS签到器"""
    
    def __init__(self):
        super().__init__("GLaDOS")
        
        # 获取配置
        config = get_glados_config()
        if not config:
            raise ValueError("未配置GLaDOS")
        
        self.cookies = config.get('cookies', [])
        
        if not self.cookies:
            raise ValueError("GLaDOS配置不完整")
    
    def checkin(self) -> List[Dict[str, Any]]:
        """执行签到"""
        results = []
        
        for i, cookie in enumerate(self.cookies):
            if not cookie:
                results.append({
                    'success': False,
                    'account': f'Account_{i+1}',
                    'message': 'Cookie为空'
                })
                continue
            
            try:
                success, message = self._sign_account(cookie)
                results.append({
                    'success': success,
                    'account': f'Account_{i+1}',
                    'message': message
                })
                logger.info(f"GLaDOS Account_{i+1}: {'成功' if success else '失败'} - {message}")
            except Exception as e:
                results.append({
                    'success': False,
                    'account': f'Account_{i+1}',
                    'message': f'异常: {str(e)}'
                })
                logger.error(f"GLaDOS Account_{i+1} 签到异常: {e}")
        
        return results
    
    def _sign_account(self, cookie: str) -> tuple[bool, str]:
        """单个账户签到"""
        session = requests.session()
        check_url = 'https://glados.rocks/api/user/checkin'
        
        headers = {
            'cookie': cookie,
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        data = {
            'token': 'glados.network'
        }
        
        # 签到
        response = session.post(url=check_url, headers=headers, json=data, timeout=10)
        response.raise_for_status()
        result = response.json()
        
        message = result.get('message', '未知')
        success = result.get('code') == 0
        
        return success, message 