"""
SSPanel 签到模块
"""

import requests
import logging
from typing import Dict, Any, List
from base_checkin import BaseCheckin
from config import get_sspanel_config

logger = logging.getLogger(__name__)


class SSPanelCheckin(BaseCheckin):
    """SSPanel签到器"""
    
    def __init__(self):
        super().__init__("SSPanel")
        
        # 获取配置
        config = get_sspanel_config()
        if not config:
            raise ValueError("未配置SSPanel")
        
        self.url = config.get('url', '')
        self.accounts = config.get('accounts', [])
        
        if not self.url or not self.accounts:
            raise ValueError("SSPanel配置不完整")
    
    def checkin(self) -> List[Dict[str, Any]]:
        """执行签到"""
        results = []
        
        for account in self.accounts:
            email = account.get('email', '')
            password = account.get('password', '')
            
            if not email or not password:
                results.append({
                    'success': False,
                    'account': email or 'unknown',
                    'message': '配置不完整'
                })
                continue
            
            try:
                success, message = self._sign_account(email, password)
                results.append({
                    'success': success,
                    'account': email,
                    'message': message
                })
            except Exception as e:
                results.append({
                    'success': False,
                    'account': email,
                    'message': f'异常: {str(e)}'
                })
        
        return results
    
    def _sign_account(self, email: str, password: str) -> tuple[bool, str]:
        """单个账户签到"""
        session = requests.session()
        login_url = f'{self.url}/auth/login'
        check_url = f'{self.url}/user/checkin'
        
        headers = {
            'origin': self.url,
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        data = {
            'email': email,
            'passwd': password
        }
        
        # 登录
        login_response = session.post(url=login_url, headers=headers, data=data, timeout=10)
        login_response.raise_for_status()
        login_result = login_response.json()
        
        if login_result.get('ret') != 1:
            return False, f"登录失败: {login_result.get('msg', '未知错误')}"
        
        # 签到
        checkin_response = session.post(url=check_url, headers=headers, timeout=10)
        checkin_response.raise_for_status()
        checkin_result = checkin_response.json()
        
        message = checkin_result.get('msg', '未知')
        success = checkin_result.get('ret') == 0
        
        return success, message 