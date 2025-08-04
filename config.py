"""
配置管理器
从GitHub Secrets读取配置
"""

import json
import os
import logging

logger = logging.getLogger(__name__)


def get_config(config_name: str):
    """
    获取配置
    
    Args:
        config_name: 配置名称 (sspanel/glados/notify)
        
    Returns:
        dict: 配置字典，如果获取失败返回None
    """
    env_var = f'{config_name.upper()}_CONFIG_JSON'
    
    try:
        config_json = os.environ.get(env_var, '')
        if config_json:
            config = json.loads(config_json)
            logger.info(f"{config_name} 配置加载成功")
            return config
        else:
            logger.warning(f"未配置 {env_var}")
            return None
    except Exception as e:
        logger.error(f"{config_name} 配置加载失败: {e}")
        return None


# 为了向后兼容，保留原有的方法名
def get_sspanel_config():
    """获取SSPanel配置"""
    return get_config('sspanel')


def get_glados_config():
    """获取GLaDOS配置"""
    return get_config('glados')


def get_notify_config():
    """获取通知配置"""
    return get_config('notify') 