"""
自动签到基础接口模块
定义所有签到网站需要实现的抽象接口
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class AccountInfo:
    """账户信息类"""
    
    def __init__(self, account_id: str, username: str = "", email: str = "", **kwargs):
        self.account_id = account_id
        self.username = username
        self.email = email
        self.extra_info = kwargs
    
    def __str__(self):
        return f"AccountInfo(id={self.account_id}, username={self.username}, email={self.email})"


class CheckinResult:
    """签到结果类"""
    
    def __init__(self, success: bool, message: str, data: Optional[Dict[str, Any]] = None):
        self.success = success
        self.message = message
        self.data = data or {}
    
    def __str__(self):
        return f"CheckinResult(success={self.success}, message='{self.message}')"


class BaseCheckin(ABC):
    """签到网站基础抽象类"""
    
    def __init__(self, name: str):
        self.name = name
        self.logger = logging.getLogger(f"{__name__}.{name}")
        self.accounts: List[AccountInfo] = []
    
    @abstractmethod
    def checkin(self, **kwargs) -> CheckinResult:
        """
        执行签到操作
        
        Args:
            **kwargs: 签到所需的参数（如用户名、密码、cookie等）
            
        Returns:
            CheckinResult: 签到结果
        """
        pass
    
    @abstractmethod
    def get_status(self, **kwargs) -> Dict[str, Any]:
        """
        获取账户状态信息
        
        Args:
            **kwargs: 获取状态所需的参数
            
        Returns:
            Dict[str, Any]: 状态信息
        """
        pass
    
    def validate_config(self, **kwargs) -> bool:
        """
        验证配置参数
        
        Args:
            **kwargs: 配置参数
            
        Returns:
            bool: 配置是否有效
        """
        return True
    
    def get_accounts(self) -> List[AccountInfo]:
        """
        获取所有账户信息
        
        Returns:
            List[AccountInfo]: 账户信息列表
        """
        return self.accounts
    
    def add_account(self, account: AccountInfo):
        """
        添加账户
        
        Args:
            account: 账户信息
        """
        self.accounts.append(account)
        self.logger.info(f"添加账户: {account}")
    
    def remove_account(self, account_id: str):
        """
        移除账户
        
        Args:
            account_id: 账户ID
        """
        self.accounts = [acc for acc in self.accounts if acc.account_id != account_id]
        self.logger.info(f"移除账户: {account_id}")
    
    def get_account_count(self) -> int:
        """
        获取账户数量
        
        Returns:
            int: 账户数量
        """
        return len(self.accounts)
    
    def format_message(self, result: CheckinResult) -> str:
        """
        格式化签到结果消息
        
        Args:
            result: 签到结果
            
        Returns:
            str: 格式化后的消息
        """
        status = "成功" if result.success else "失败"
        account_count = result.data.get('total_accounts', 0)
        success_count = result.data.get('success_accounts', 0)
        
        if account_count > 1:
            return f"[{self.name}] 签到{status}: {success_count}/{account_count} 个账户 - {result.message}"
        else:
            return f"[{self.name}] 签到{status}: {result.message}"
    
    def _get_timestamp(self) -> str:
        """获取当前时间戳"""
        from datetime import datetime
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S') 