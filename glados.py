"""
GLaDOS 签到模块
"""

import requests
from typing import Dict, Any, List
from base_checkin import BaseCheckin
from config import get_glados_config
import json


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
                    'account': f'account_{i+1}',
                    'message': 'cookie 为空'
                })
                continue
            
            try:
                success, message = self._sign_account(cookie)
                results.append({
                    'success': success,
                    'account': f'account_{i+1}',
                    'message': message
                })
            except Exception as e:
                results.append({
                    'success': False,
                    'account': f'account_{i+1}',
                    'message': f'异常: {str(e)}'
                })
        
        return results
    
    def _sign_account(self, cookie: str) -> tuple[bool, str]:
        """单个账户签到"""
        session = requests.session()
        checkin_url = "https://glados.rocks/api/user/checkin"
        headers = {
            'cookie': cookie,
            'referer': 'https://glados.rocks/console/checkin',
            'origin': 'https://glados.rocks',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36',
            'content-type': 'application/json;charset=UTF-8'
        }
        payload = {'token': 'glados.one'}

        # 签到
        checkin_resp = session.post(checkin_url, headers=headers, data=json.dumps(payload), timeout=20)
        checkin_resp.raise_for_status()
        checkin_json = checkin_resp.json()

        success = checkin_json.get('code') == 0
        msg = checkin_json.get('message')
        if "Repeats" in msg:
            success = True

        return success, msg