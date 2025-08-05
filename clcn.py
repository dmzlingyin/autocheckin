"""
clcn 首图图书馆签到模块
"""

from typing import Dict, Any, List
from base_checkin import BaseCheckin
from config import get_clcn_config
from playwright.sync_api import sync_playwright
import logging
import ddddocr

logger = logging.getLogger(__name__)


class CLCNCheckin(BaseCheckin):
    """CLCN 签到器"""
    
    def __init__(self):
        super().__init__("CLCN")
        
        # 获取配置
        config = get_clcn_config()
        if not config:
            raise ValueError("未配置 CLCN")
        
        self.url = config.get('url', 'https://www.clcn.net.cn')
        self.accounts = config.get('accounts', [])
        
        if not self.url or not self.accounts:
            raise ValueError("CLCN 配置不完整")
    
    def checkin(self) -> List[Dict[str, Any]]:
        """执行签到"""
        results = []
        
        for account in self.accounts:
            reader_card = account.get('reader_card', '')
            password = account.get('password', '')
            
            if not reader_card or not password:
                results.append({
                    'success': False,
                    'account': reader_card or 'unknown',
                    'message': '配置不完整'
                })
                continue
            
            try:
                success, message = self._sign_account(reader_card, password)
                results.append({
                    'success': success,
                    'account': reader_card,
                    'message': message
                })
            except Exception as e:
                results.append({
                    'success': False,
                    'account': reader_card,
                    'message': f'异常: {str(e)}'
                })
        
        return results

    def _sign_account(self, reader_card: str, password: str, max_retries: int = 3) -> tuple[bool, str]:
        """单个账户签到"""
        try:
            with sync_playwright() as playwright:
                logger.info(f"开始首都图书馆账号 {reader_card} 的签到流程")

                # 启动浏览器
                browser = playwright.chromium.launch(headless=False)
                page = browser.new_page()

                # 先访问首页
                logger.info(f"访问首页: {self.url}")
                page.goto(self.url)

                # 等待页面加载完成
                page.wait_for_load_state("networkidle")

                # 点击用户登录链接
                logger.info("点击用户登录链接")
                login_link = page.query_selector("li.clcn-user-login a")
                if login_link:
                    login_link.click()
                    logger.info("成功点击登录链接")
                else:
                    # 如果找不到链接，直接访问登录页面作为备选方案
                    login_url = f"{self.url}/user/auth/login"
                    logger.info(f"未找到登录链接，直接访问登录页面: {login_url}")
                    page.goto(login_url)

                # 填写读者卡号
                logger.info(f"填写读者卡号: {reader_card}")
                page.fill("#loginform-username", reader_card)

                # 填写密码
                logger.info("填写密码")
                page.fill("#loginform-password", password)

                # 尝试登录，最多重试 max_retries 次
                for attempt in range(max_retries):
                    logger.info(f"尝试第 {attempt + 1} 次登录")

                    # 处理验证码
                    captcha_text = ""
                    try:
                        captcha_element = page.query_selector("#loginform-verifycode-image")
                        if not captcha_element:
                            captcha_element = page.query_selector("img[alt='验证码']")

                        if captcha_element:
                            captcha_url = captcha_element.get_attribute("src")
                            if captcha_url:
                                if captcha_url.startswith("/"):
                                    base_url = "https://www.clcn.net.cn"
                                    captcha_url = f"{base_url}{captcha_url}"

                                logger.info(f"验证码URL: {captcha_url}")

                                # 导入OCR模块
                                from ocr import recognize_online_image

                                # 在同一个浏览器会话中请求图片
                                img_response = page.request.get(captcha_url)
                                img_data = img_response.body()

                                ocr = ddddocr.DdddOcr()
                                captcha_text = ocr.classification(img_data)
                                logger.info(f"验证码识别结果: {captcha_text}")

                                if captcha_text:
                                    logger.info(f"填写验证码: {captcha_text}")
                                    page.fill("#loginform-verifycode", captcha_text)
                                else:
                                    logger.warning("验证码识别失败")
                            else:
                                logger.warning("验证码图片URL为空")
                        else:
                            logger.warning("未找到验证码图片元素")
                    except Exception as e:
                        logger.error(f"处理验证码时出错: {e}")

                    # 点击登录按钮
                    logger.info("点击登录按钮")
                    page.click("button[name='login-button']")

                    # 等待页面加载
                    page.wait_for_timeout(5000)

                    # 检查是否登录成功
                    if "登录失败" in page.content():
                        logger.error("登录失败，请重试")
                        if attempt < max_retries - 1:
                            continue  # 重试登录
                        else:
                            browser.close()
                            return False, "登录失败，请检查账号密码"
                    
                    # 检查是否已签到
                    if "已签到" in page.content():
                        logger.info("用户已经签到，直接返回成功")
                        browser.close()
                        return True, "已签到，返回成功"

                    break  # 登录成功，跳出重试循环

                # 点击签到按钮
                try:
                    logger.info("尝试点击签到按钮")
                    page.click("button.btn.btn-primary.btn-sign")
                    logger.info("签到按钮点击成功")

                    # 等待签到结果
                    page.wait_for_timeout(3000)

                    # 检查签到结果
                    if "签到成功" in page.content():
                        message = "签到成功"
                    else:
                        message = "可能已经签到过了"

                    browser.close()
                    return True, message

                except Exception as e:
                    logger.warning(f"签到按钮未找到或已签到: {e}")
                    browser.close()
                    return True, "可能已经签到过了或找不到签到按钮"

        except Exception as e:
            logger.error(f"签到过程发生异常: {e}")
            return False, f"签到异常: {str(e)}"