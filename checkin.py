"""
主程序
简化的签到管理器
"""

import logging
from typing import List, Dict, Any
from base_checkin import BaseCheckin
from sspanel import SSPanelCheckin
from glados import GLaDOSCheckin

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CheckinManager:
    """签到管理器"""
    
    def __init__(self):
        self.checkers: List[BaseCheckin] = []
        self._init_checkers()
    
    def _init_checkers(self):
        """初始化签到器"""
        # 添加SSPanel签到器
        try:
            sspanel = SSPanelCheckin()
            self.checkers.append(sspanel)
            logger.info("SSPanel签到器初始化成功")
        except Exception as e:
            logger.warning(f"SSPanel签到器初始化失败: {e}")
        
        
        # 添加GLaDOS签到器
        try:
            glados = GLaDOSCheckin()
            self.checkers.append(glados)
            logger.info("GLaDOS签到器初始化成功")
        except Exception as e:
            logger.warning(f"GLaDOS签到器初始化失败: {e}")
    
    def run_all(self) -> List[Dict[str, Any]]:
        """执行所有签到器"""
        all_results = []
        
        for checker in self.checkers:
            try:
                logger.info(f"开始执行 {checker.get_name()} 签到")
                results = checker.checkin()
                all_results.extend(results)
                
                # 统计当前签到器结果
                success_count = sum(1 for r in results if r['success'])
                total_count = len(results)
                logger.info(f"{checker.get_name()} 完成: {success_count}/{total_count} 成功")
                
            except Exception as e:
                logger.error(f"{checker.get_name()} 执行异常: {e}")
                all_results.append({
                    'success': False,
                    'account': checker.get_name(),
                    'message': f'执行异常: {str(e)}'
                })
        
        return all_results
    
    def run_specific(self, checker_name: str) -> List[Dict[str, Any]]:
        """执行指定签到器"""
        for checker in self.checkers:
            if checker.get_name().lower() == checker_name.lower():
                logger.info(f"开始执行 {checker.get_name()} 签到")
                return checker.checkin()
        
        logger.error(f"未找到签到器: {checker_name}")
        return []


def main():
    """主函数"""
    logger.info("自动签到开始")
    
    manager = CheckinManager()
    
    if not manager.checkers:
        logger.error("没有可用的签到器")
        return
    
    # 执行签到
    results = manager.run_all()
    
    # 统计结果
    success_count = sum(1 for r in results if r['success'])
    total_count = len(results)
    
    logger.info(f"签到完成: {success_count}/{total_count} 成功")
    
    # 输出详细结果
    for result in results:
        status = "成功" if result['success'] else "失败"
        logger.info(f"{result['account']}: {status} - {result['message']}")


if __name__ == "__main__":
    main()
