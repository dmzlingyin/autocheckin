"""
GLaDOS 签到模块
支持GLaDOS机场自动签到
"""

import requests
import json
import os
import logging
from typing import Dict, Any, List
from base_checkin import BaseCheckin, CheckinResult, AccountInfo
from config_manager import get_config_manager

logger = logging.getLogger(__name__)


class GLaDOSCheckin(BaseCheckin):
    """GLaDOS签到类"""
    
    def __init__(self):
        super().__init__("GLaDOS")
        
        # 使用配置管理器获取配置
        config_manager = get_config_manager()
        config = config_manager.get_glados_config()
        
        if not config:
            raise ValueError("未配置GLaDOS相关环境变量")
        
        self.cookies = config.get('cookies', [])
        
        if not self.cookies:
            raise ValueError("未配置GLaDOS Cookie")
        
        # 初始化账户信息
        self._init_accounts()
    
    def _init_accounts(self):
        """初始化账户信息"""
        for i, cookie in enumerate(self.cookies):
            # 尝试从cookie中提取邮箱信息
            email = self._extract_email_from_cookie(cookie)
            account_info = AccountInfo(
                account_id=f"glados_{i}",
                email=email or f"glados_account_{i}",
                username=email.split('@')[0] if email and '@' in email else f"glados_user_{i}",
                extra_info={'cookie_index': i}
            )
            self.add_account(account_info)
    
    def _extract_email_from_cookie(self, cookie: str) -> str:
        """从cookie中提取邮箱信息"""
        try:
            # 尝试解析cookie中的邮箱信息
            if 'email=' in cookie:
                email_part = cookie.split('email=')[1].split(';')[0]
                return email_part
        except:
            pass
        return ""
    
    def validate_config(self, **kwargs) -> bool:
        """验证配置"""
        if not self.cookies:
            return False
        
        return True
    
    def checkin(self, **kwargs) -> CheckinResult:
        """执行签到"""
        try:
            if not self.validate_config():
                return CheckinResult(False, "配置验证失败", {
                    'site_name': self.name,
                    'timestamp': self._get_timestamp()
                })
            
            if not self.cookies:
                return CheckinResult(False, "没有找到有效的Cookie配置", {
                    'site_name': self.name,
                    'timestamp': self._get_timestamp()
                })
            
            results = []
            for i, cookie in enumerate(self.cookies):
                result = self._sign_account(i, cookie)
                results.append(result)
            
            # 统计结果
            success_count = sum(1 for r in results if r['success'])
            total_count = len(results)
            
            if success_count == total_count:
                message = f"所有账户签到成功 ({success_count}/{total_count})"
            elif success_count > 0:
                message = f"部分账户签到成功 ({success_count}/{total_count})"
            else:
                message = f"所有账户签到失败 ({success_count}/{total_count})"
            
            return CheckinResult(success_count > 0, message, {
                'site_name': self.name,
                'timestamp': self._get_timestamp(),
                'total_accounts': total_count,
                'success_accounts': success_count,
                'details': results
            })
            
        except Exception as e:
            self.logger.error(f"GLaDOS签到异常: {e}")
            return CheckinResult(False, f"签到异常: {str(e)}", {
                'site_name': self.name,
                'timestamp': self._get_timestamp()
            })
    
    def _sign_account(self, order: int, cookie: str) -> Dict[str, Any]:
        """单个账户签到"""
        checkin_url = "https://glados.rocks/api/user/checkin"
        status_url = "https://glados.rocks/api/user/status"
        
        headers = {
            'cookie': cookie,
            'referer': 'https://glados.rocks/console/checkin',
            'origin': 'https://glados.rocks',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36',
            'content-type': 'application/json;charset=UTF-8'
        }
        
        payload = {
            'token': 'glados.one'
        }
        
        try:
            self.logger.info(f'===账号{order}进行签到...===')
            
            # 签到
            checkin_response = requests.post(
                checkin_url, 
                headers=headers, 
                data=json.dumps(payload), 
                timeout=10
            )
            checkin_response.raise_for_status()
            
            # 获取状态
            status_response = requests.get(status_url, headers=headers, timeout=10)
            status_response.raise_for_status()
            
            # 解析结果
            checkin_result = checkin_response.json()
            status_result = status_response.json()
            
            # 获取用户信息
            email = status_result.get('data', {}).get('email', '未知')
            left_days = status_result.get('data', {}).get('leftDays', '0')
            left_days = left_days.split('.')[0] if isinstance(left_days, str) else str(left_days)
            
            # 检查签到结果
            if 'message' in checkin_result:
                message = checkin_result['message']
                success = True
                self.logger.info(f"{email}----结果--{message}----剩余({left_days})天")
            else:
                message = "Cookie已失效"
                success = False
                self.logger.warning(f"{email}----{message}")
            
            return {
                'success': success,
                'email': email,
                'message': message,
                'left_days': left_days,
                'account_id': f"glados_{order}"
            }
            
        except Exception as e:
            self.logger.error(f"账号{order}签到异常: {e}")
            return {
                'success': False,
                'email': f'账号{order}',
                'message': f"签到异常: {str(e)}",
                'left_days': '0',
                'account_id': f"glados_{order}"
            }
    
    def get_status(self, **kwargs) -> Dict[str, Any]:
        """获取账户状态"""
        status_info = []
        
        for i, cookie in enumerate(self.cookies):
            try:
                status_url = "https://glados.rocks/api/user/status"
                headers = {
                    'cookie': cookie,
                    'referer': 'https://glados.rocks/console/checkin',
                    'origin': 'https://glados.rocks',
                    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'
                }
                
                response = requests.get(status_url, headers=headers, timeout=10)
                response.raise_for_status()
                
                result = response.json()
                data = result.get('data', {})
                
                email = data.get('email', f'账号{i}')
                left_days = data.get('leftDays', '0')
                level = data.get('level', '0')
                
                status_info.append({
                    'account_id': f"glados_{i}",
                    'email': email,
                    'username': email.split('@')[0] if '@' in email else f"glados_user_{i}",
                    'left_days': left_days,
                    'level': level,
                    'status': 'active'
                })
                
            except Exception as e:
                self.logger.error(f"获取账号{i}状态失败: {e}")
                status_info.append({
                    'account_id': f"glados_{i}",
                    'email': f'账号{i}',
                    'username': f"glados_user_{i}",
                    'left_days': '0',
                    'level': '0',
                    'status': 'error'
                })
        
        return {
            'site_name': self.name,
            'url': 'https://glados.rocks',
            'account_count': len(self.cookies),
            'accounts': status_info
        }
    
    def _get_timestamp(self) -> str:
        """获取当前时间戳"""
        from datetime import datetime
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S') 