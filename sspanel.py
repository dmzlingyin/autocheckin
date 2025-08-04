"""
SSPanel 机场签到模块
支持基于SSPanel的机场自动签到
"""

import requests
import json
import os
import logging
from typing import Dict, Any, List
from base_checkin import BaseCheckin, CheckinResult, AccountInfo
from config import get_config_manager

logger = logging.getLogger(__name__)


class SSPanelCheckin(BaseCheckin):
    """SSPanel机场签到类"""
    
    def __init__(self):
        super().__init__("SSPanel")
        
        # 使用配置管理器获取配置
        config_manager = get_config_manager()
        config = config_manager.get_sspanel_config()
        
        if not config:
            raise ValueError("未配置SSPanel相关环境变量")
        
        self.url = config.get('url', '')
        self.accounts = config.get('accounts', [])
        
        if not self.url:
            raise ValueError("未配置SSPanel URL")
        if not self.accounts:
            raise ValueError("未配置SSPanel账户信息")
        
        # 初始化账户信息
        self._init_accounts()
    
    def _init_accounts(self):
        """初始化账户信息"""
        for i, account in enumerate(self.accounts):
            account_info = AccountInfo(
                account_id=f"sspanel_{i}",
                email=account.get('email', ''),
                username=account.get('email', '').split('@')[0] if '@' in account.get('email', '') else account.get('email', '')
            )
            self.add_account(account_info)
    
    def validate_config(self, **kwargs) -> bool:
        """验证配置"""
        if not self.url or not self.accounts:
            return False
        
        for account in self.accounts:
            if not account.get('email') or not account.get('password'):
                self.logger.error("SSPanel账户配置不完整，需要email和password")
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
            
            if not self.accounts:
                return CheckinResult(False, "没有找到有效的账户配置", {
                    'site_name': self.name,
                    'timestamp': self._get_timestamp()
                })
            
            results = []
            for i, account in enumerate(self.accounts):
                result = self._sign_account(i, account)
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
            self.logger.error(f"SSPanel签到异常: {e}")
            return CheckinResult(False, f"签到异常: {str(e)}", {
                'site_name': self.name,
                'timestamp': self._get_timestamp()
            })
    
    def _sign_account(self, order: int, account: Dict[str, str]) -> Dict[str, Any]:
        """单个账户签到"""
        session = requests.session()
        
        login_url = f'{self.url}/auth/login'
        check_url = f'{self.url}/user/checkin'
        
        headers = {
            'origin': self.url,
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'
        }
        
        data = {
            'email': account['email'],
            'passwd': account['password']
        }
        
        try:
            self.logger.info(f'===账号{order}进行登录...===')
            self.logger.info(f'账号：{account["email"]}')
            
            # 登录
            login_response = session.post(url=login_url, headers=headers, data=data, timeout=10)
            login_response.raise_for_status()
            
            login_result = login_response.json()
            self.logger.info(f"登录结果: {login_result.get('msg', '未知')}")
            
            if login_result.get('ret') != 1:
                return {
                    'success': False,
                    'email': account['email'],
                    'message': f"登录失败: {login_result.get('msg', '未知错误')}",
                    'account_id': f"sspanel_{order}"
                }
            
            # 签到
            checkin_response = session.post(url=check_url, headers=headers, timeout=10)
            checkin_response.raise_for_status()
            
            checkin_result = checkin_response.json()
            message = checkin_result.get('msg', '未知')
            self.logger.info(f"签到结果: {message}")
            
            return {
                'success': checkin_result.get('ret') == 1,
                'email': account['email'],
                'message': message,
                'account_id': f"sspanel_{order}"
            }
            
        except Exception as e:
            self.logger.error(f"账号{order}签到异常: {e}")
            return {
                'success': False,
                'email': account['email'],
                'message': f"签到异常: {str(e)}",
                'account_id': f"sspanel_{order}"
            }
    
    def get_status(self, **kwargs) -> Dict[str, Any]:
        """获取账户状态"""
        account_status = []
        
        for i, account in enumerate(self.accounts):
            account_status.append({
                'account_id': f"sspanel_{i}",
                'email': account.get('email', ''),
                'username': account.get('email', '').split('@')[0] if '@' in account.get('email', '') else account.get('email', ''),
                'status': 'configured'
            })
        
        return {
            'site_name': self.name,
            'url': self.url,
            'account_count': len(self.accounts),
            'accounts': account_status
        }
    
    def _get_timestamp(self) -> str:
        """获取当前时间戳"""
        from datetime import datetime
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S') 