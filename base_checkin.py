"""
签到基础接口
简化的抽象层，只保留核心的checkin方法
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class BaseCheckin(ABC):
    """签到基础类"""
    
    def __init__(self, name: str):
        self.name = name
        self.logger = logging.getLogger(f"{__name__}.{name}")
    
    @abstractmethod
    def checkin(self) -> List[Dict[str, Any]]:
        """
        执行签到操作
        
        Returns:
            List[Dict[str, Any]]: 签到结果列表，每个结果包含：
                - success: bool - 是否成功
                - account: str - 账户标识
                - message: str - 结果消息
        """
        pass
    
    def get_name(self) -> str:
        """获取签到器名称"""
        return self.name 