"""
自动签到主程序
支持多网站签到，统一管理和通知
"""

import os
import sys
import logging
from typing import List, Dict, Any
from datetime import datetime

# 导入基础模块
from base_checkin import BaseCheckin, CheckinResult, AccountInfo
from notify import NotifyManager, create_notify_manager

# 导入签到模块
from sspanel import SSPanelCheckin
from glados import GLaDOSCheckin

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('checkin.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)


class CheckinManager:
    """签到管理器"""
    
    def __init__(self):
        self.checkers: Dict[str, BaseCheckin] = {}
        self.notify_manager = create_notify_manager()
        self.logger = logging.getLogger(__name__)
    
    def register_checker(self, name: str, checker: BaseCheckin):
        """
        注册签到器
        
        Args:
            name: 签到器名称
            checker: 签到器实例
        """
        self.checkers[name] = checker
        self.logger.info(f"注册签到器: {name}")
    
    def get_available_checkers(self) -> List[str]:
        """获取可用的签到器列表"""
        return list(self.checkers.keys())
    
    def get_total_accounts(self) -> int:
        """获取所有签到器的总账户数"""
        total = 0
        for checker in self.checkers.values():
            total += checker.get_account_count()
        return total
    
    def print_account_summary(self):
        """打印账户摘要信息"""
        logger.info("=== 账户信息摘要 ===")
        total_accounts = 0
        
        for name, checker in self.checkers.items():
            account_count = checker.get_account_count()
            total_accounts += account_count
            logger.info(f"{name}: {account_count} 个账户")
            
            # 显示账户详情
            accounts = checker.get_accounts()
            for account in accounts:
                logger.info(f"  - {account.email} ({account.username})")
        
        logger.info(f"总计: {total_accounts} 个账户")
        logger.info("==================")
    
    def run_checkin(self, checker_names: List[str] = None) -> List[CheckinResult]:
        """
        执行签到
        
        Args:
            checker_names: 要执行的签到器名称列表，为None时执行所有
            
        Returns:
            List[CheckinResult]: 签到结果列表
        """
        if checker_names is None:
            checker_names = list(self.checkers.keys())
        
        results = []
        
        for name in checker_names:
            if name not in self.checkers:
                self.logger.warning(f"未找到签到器: {name}")
                continue
            
            checker = self.checkers[name]
            account_count = checker.get_account_count()
            self.logger.info(f"开始执行 {name} 签到... (账户数: {account_count})")
            
            try:
                result = checker.checkin()
                results.append(result)
                self.logger.info(f"{name} 签到完成: {result.message}")
            except Exception as e:
                self.logger.error(f"{name} 签到异常: {e}")
                error_result = CheckinResult(False, f"签到异常: {str(e)}", {
                    'site_name': name,
                    'timestamp': self._get_timestamp()
                })
                results.append(error_result)
        
        return results
    
    def send_notifications(self, results: List[CheckinResult]):
        """发送通知"""
        if not results:
            self.logger.info("没有签到结果，跳过通知")
            return
        
        try:
            notify_results = self.notify_manager.send_checkin_results(results)
            
            for result in notify_results:
                if result.success:
                    self.logger.info(f"{result.platform} 通知发送成功")
                else:
                    self.logger.warning(f"{result.platform} 通知发送失败: {result.message}")
                    
        except Exception as e:
            self.logger.error(f"发送通知异常: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """获取所有签到器状态"""
        status = {
            'total_checkers': len(self.checkers),
            'total_accounts': self.get_total_accounts(),
            'available_checkers': self.get_available_checkers(),
            'checkers_status': {}
        }
        
        for name, checker in self.checkers.items():
            try:
                checker_status = checker.get_status()
                checker_status['account_count'] = checker.get_account_count()
                status['checkers_status'][name] = checker_status
            except Exception as e:
                self.logger.error(f"获取 {name} 状态失败: {e}")
                status['checkers_status'][name] = {'error': str(e)}
        
        return status
    
    def print_detailed_status(self):
        """打印详细状态信息"""
        logger.info("=== 详细状态信息 ===")
        status = self.get_status()
        
        logger.info(f"签到器总数: {status['total_checkers']}")
        logger.info(f"账户总数: {status['total_accounts']}")
        logger.info(f"可用签到器: {', '.join(status['available_checkers'])}")
        
        for name, checker_status in status['checkers_status'].items():
            logger.info(f"\n{name}:")
            if 'error' in checker_status:
                logger.info(f"  状态: 错误 - {checker_status['error']}")
            else:
                logger.info(f"  账户数: {checker_status.get('account_count', 0)}")
                logger.info(f"  网站: {checker_status.get('url', '未知')}")
                
                accounts = checker_status.get('accounts', [])
                for account in accounts:
                    logger.info(f"    - {account.get('email', '未知')} ({account.get('status', '未知状态')})")
        
        logger.info("==================")
    
    def _get_timestamp(self) -> str:
        """获取当前时间戳"""
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def create_checkin_manager() -> CheckinManager:
    """
    创建签到管理器并注册所有签到器
    
    Returns:
        CheckinManager: 配置好的签到管理器
    """
    manager = CheckinManager()
    
    # 注册SSPanel签到器
    try:
        sspanel_checker = SSPanelCheckin()
        manager.register_checker("SSPanel", sspanel_checker)
        logger.info("SSPanel签到器注册成功")
    except Exception as e:
        logger.warning(f"SSPanel签到器注册失败: {e}")
    
    # 注册GLaDOS签到器
    try:
        glados_checker = GLaDOSCheckin()
        manager.register_checker("GLaDOS", glados_checker)
        logger.info("GLaDOS签到器注册成功")
    except Exception as e:
        logger.warning(f"GLaDOS签到器注册失败: {e}")
    
    return manager


def main():
    """主函数"""
    logger.info("=== 自动签到程序启动 ===")
    
    try:
        # 创建签到管理器
        manager = create_checkin_manager()
        
        # 检查是否有可用的签到器
        available_checkers = manager.get_available_checkers()
        if not available_checkers:
            logger.error("没有可用的签到器，请检查配置")
            return
        
        # 显示账户摘要
        manager.print_account_summary()
        
        # 显示详细状态（可选）
        if os.environ.get('SHOW_DETAILED_STATUS', 'false').lower() == 'true':
            manager.print_detailed_status()
        
        logger.info(f"可用签到器: {', '.join(available_checkers)}")
        
        # 检查是否指定了特定的签到器（手动触发时）
        specified_checkers = os.environ.get('CHECKERS', '').strip()
        if specified_checkers:
            checker_names = [name.strip() for name in specified_checkers.split(',') if name.strip()]
            # 验证指定的签到器是否存在
            invalid_checkers = [name for name in checker_names if name not in available_checkers]
            if invalid_checkers:
                logger.error(f"指定的签到器不存在: {', '.join(invalid_checkers)}")
                logger.info(f"可用的签到器: {', '.join(available_checkers)}")
                return
            
            logger.info(f"手动触发，执行指定签到器: {', '.join(checker_names)}")
            results = manager.run_checkin(checker_names)
        else:
            logger.info("执行所有可用签到器")
            results = manager.run_checkin()
        
        # 统计结果
        success_count = sum(1 for r in results if r.success)
        total_count = len(results)
        
        logger.info(f"签到完成: {success_count}/{total_count} 成功")
        
        # 发送通知
        manager.send_notifications(results)
        
        logger.info("=== 自动签到程序结束 ===")
        
    except Exception as e:
        logger.error(f"程序执行异常: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
