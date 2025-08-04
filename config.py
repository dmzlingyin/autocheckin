"""
配置管理器
支持JSON格式的GitHub Secrets配置
"""

import json
import os
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class ConfigManager:
    """配置管理器"""
    
    def __init__(self):
        self.configs = {}
        self._load_configs()
    
    def _load_configs(self):
        """加载所有配置"""
        # 加载SSPanel配置
        self._load_sspanel_config()
        
        # 加载GLaDOS配置
        self._load_glados_config()
        
        # 加载通知配置
        self._load_notify_config()
    
    def _load_sspanel_config(self):
        """加载SSPanel配置"""
        try:
            sspanel_json = os.environ.get('SSPANEL_CONFIG_JSON', '')
            if sspanel_json:
                config = json.loads(sspanel_json)
                self.configs['sspanel'] = {
                    'url': config.get('url', ''),
                    'accounts': config.get('accounts', [])
                }
                logger.info("SSPanel配置加载成功")
            else:
                logger.warning("未配置SSPANEL_CONFIG_JSON")
                
        except Exception as e:
            logger.error(f"SSPanel配置加载失败: {e}")
    
    def _load_glados_config(self):
        """加载GLaDOS配置"""
        try:
            glados_json = os.environ.get('GLADOS_CONFIG_JSON', '')
            if glados_json:
                config = json.loads(glados_json)
                self.configs['glados'] = {
                    'cookies': config.get('cookies', [])
                }
                logger.info("GLaDOS配置加载成功")
            else:
                logger.warning("未配置GLADOS_CONFIG_JSON")
                
        except Exception as e:
            logger.error(f"GLaDOS配置加载失败: {e}")
    
    def _load_notify_config(self):
        """加载通知配置"""
        try:
            notify_json = os.environ.get('NOTIFY_CONFIG_JSON', '')
            if notify_json:
                config = json.loads(notify_json)
                self.configs['notify'] = config
                logger.info("通知配置加载成功")
            else:
                logger.warning("未配置NOTIFY_CONFIG_JSON")
                
        except Exception as e:
            logger.error(f"通知配置加载失败: {e}")
    
    def get_sspanel_config(self) -> Optional[Dict[str, Any]]:
        """获取SSPanel配置"""
        return self.configs.get('sspanel')
    
    def get_glados_config(self) -> Optional[Dict[str, Any]]:
        """获取GLaDOS配置"""
        return self.configs.get('glados')
    
    def get_notify_config(self) -> Optional[Dict[str, Any]]:
        """获取通知配置"""
        return self.configs.get('notify')
    
    def get_all_configs(self) -> Dict[str, Any]:
        """获取所有配置"""
        return self.configs
    
    def validate_config(self, config_name: str) -> bool:
        """验证配置是否有效"""
        config = self.configs.get(config_name)
        if not config:
            return False
        
        if config_name == 'sspanel':
            return bool(config.get('url') and config.get('accounts'))
        elif config_name == 'glados':
            return bool(config.get('cookies'))
        elif config_name == 'notify':
            return bool(config)
        
        return False


# 全局配置管理器实例
config_manager = ConfigManager()


def get_config_manager() -> ConfigManager:
    """获取配置管理器实例"""
    return config_manager 