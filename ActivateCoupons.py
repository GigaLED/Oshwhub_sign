import os

# import json
import traceback
from time import sleep
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import WebDriverException
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from loguru import logger

ENABLE_PushNnotify = True  # 消息推送开关
if ENABLE_PushNnotify:
    try:
        from notify import send
    except ModuleNotFoundError as ex:
        logger.info("notify 模块未找到，跳过推送! ")

success_count = 0

def OpenWebSite(browser: webdriver.Chrome, activate_msg: str):
    """Open the WebSite

    Args:
        browser (webdriver.Chrome): A Chrome browser instance
        activate_msg (str): activate_msg

    Returns:
        bool: Running successfully or not
        str: activate_msg
    """    
    try:
        browser.get("https://u.lceda.cn/account/user/coupon/activating")
        return True, activate_msg
    except TimeoutException as ex:
        logger.error("页面加载超时!: {}".format(ex))
        activate_msg += "页面加载超时! \n"
        return False, activate_msg
    except WebDriverException as ex:
        logger.error("页面崩溃!: {}".format(ex))
        activate_msg += "页面崩溃! \n"
        return False, activate_msg

def FindSignPage(wait: WebDriverWait, activate_msg: str):
    """Find the sign page witch use username and password

    Args:
        wait (WebDriverWait): A WebDriverWait object to wait for the browser to complete an operation.
        activate_msg (str): activate_msg

    Returns:
        bool: Running successfully or not
        str: activate_msg
    """    
    logger.info("需要登录，开始登录 ")
    # 寻找登录界面
    try:
        logger.info("寻找登录界面 ")
        PasswordEntryPage = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR,"#__layout > div > div > div > main > div > div > div:nth-child(2) > div:nth-child(1) > ul > li:nth-child(2)")))
        PasswordEntryPage.click()
        return True, activate_msg
    except Exception as ex:
        logger.error("无法登录:未找到密码登陆界面!: {}".format(ex))
        activate_msg += "无法登录:未找到密码登陆界面! \n"
        return False, activate_msg

def EnterAccount(browser: webdriver.Chrome, wait: WebDriverWait, LoginName: str, LoginPassword: str, activate_msg: str):
    """Enter account name and password to input box

    Args:
        browser (webdriver.Chrome): A Chrome browser instance
        wait (WebDriverWait): A WebDriverWait object to wait for the browser to complete an operation.
        LoginName (str): _description_
        LoginPassword (str): _description_
        activate_msg (str): activate_msg

    Returns:
        bool: Running successfully or not
        str: activate_msg
    """
    try:
        logger.info("输入账号密码 ")
        username_input = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR,"#__layout > div > div > div > main > div > div > div:nth-child(2) > div:nth-child(1) > div > div:nth-child(2) > div > form > div:nth-child(1) > div > div:nth-child(1) > div > input")))
        username_input.clear()
        username_input.send_keys(LoginName)
        password_input = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR,"#__layout > div > div > div > main > div > div > div:nth-child(2) > div:nth-child(1) > div > div:nth-child(2) > div > form > div:nth-child(2) > div > div:nth-child(1) > div > input")))
        password_input.clear()
        password_input.send_keys(LoginPassword)
        return True, activate_msg
    except Exception as ex:
        logger.error("无法登录:账号密码输入未成功!: {}".format(ex))
        activate_msg += "无法登录:账号密码输入未成功! \n"
        browser.quit()
        return False, activate_msg

def SlideToLogin(browser: webdriver.Chrome, wait: WebDriverWait, activate_msg: str):
    """Control the slidebar rto login

    Args:
        browser (webdriver.Chrome): A Chrome browser instance
        wait (WebDriverWait): A WebDriverWait object to wait for the browser to complete an operation.
        activate_msg (str): activate_msg

    Returns:
        bool: Running successfully or not
        str: activate_msg
    """
    try:
        logger.info("滑动验证并登录 ")
        slider = wait.until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="nc_1_n1z"]')))
        ActionChains(browser).drag_and_drop_by_offset(slider, 400, 0).perform()
        sleep(1)
        confirm_button = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR,"#__layout > div > div > div > main > div > div > div:nth-child(2) > div:nth-child(1) > div > div:nth-child(2) > div > button")))
        confirm_button.click()
        # 激活
        sleep(1)
        return True, activate_msg
    except Exception as ex:
        logger.error("无法登录:滑动验证或登录不成功!: {}".format(ex))
        activate_msg += "无法登录:滑动验证或登录不成功! \n"
        return False, activate_msg

def CheckCoupons(wait: WebDriverWait, activate_msg: str, CouponNum = 2):
    """Check Coupons and activate them

    Args:
        wait (WebDriverWait): A WebDriverWait object to wait for the browser to complete an operation.
        activate_msg (str): activate_msg
        CouponNum (int, optional): Coupon counts. Defaults to 3.

    Returns:
        bool: Running successfully or not
        str: activate_msg
    """    
    # //*[@id="root"]/div/main/main/div/div/div[2]/div/div[2]/div[1]/div/div[3]/div[2]/div
    # #root > div > main > main > div > div > div.main-grow > div > div.coupon-center > div.coupon-layer > div > div.coupon-foot > div.coupon-name
    # //*[@id="root"]/div/main/main/div/div/div[2]/div/div[2]/div[3]/div/div[3]/button[2]
    try:
        for i in range(CouponNum):
            sleep(1)
            global success_count
            couponFind = 0
            try:
                coupon_button = wait.until(
                    EC.presence_of_element_located((By.XPATH,'//*[@id="root"]/div/main/main/div/div/div[2]/div/div[2]/div[1]/div/div[3]/div[2]/div')))
                couponFind += 1
                coupon_name = wait.until(
                                EC.presence_of_element_located((By.CSS_SELECTOR,
                                    "#root > div > main > main > div > div > div.main-grow > div > div.coupon-center > div.coupon-layer > div > div.coupon-foot > div.coupon-name"))).text
            except NoSuchElementException as ex:
                logger.error("优惠券查找出错: {}".format(ex))
                if not couponFind:
                    activate_msg += "优惠券查找出错! \n"
                break
            except TimeoutException as ex:
                # logger.error("没有优惠券: {}".format(ex))
                logger.warning("没有优惠券!")
                if not couponFind:
                    activate_msg += "没有优惠券! \n"
                break
            coupon_button.click()
            sleep(2)
            try:
                confirm_button = wait.until(
                    EC.presence_of_element_located((By.XPATH,'//*[@id="root"]/div/main/main/div/div/div[2]/div/div[2]/div[3]/div/div[3]/button[2]')))
            except NoSuchElementException as ex:
                logger.error("找不到确认兑换按钮: {}".format(ex))
                activate_msg += "找不到确认兑换按钮! \n"
                break
            except TimeoutException as ex:
                logger.error("查找确认兑换按钮超时: {}".format(ex))
                activate_msg += "查找确认兑换按钮超时! \n"
                break
            confirm_button.click()
            if not couponFind:
                activate_msg += "已激活：{} \n".format(coupon_name)
            success_count += 1
        return True, activate_msg
    except Exception as ex:
        logger.error("激活优惠券不成功!: {}".format(ex))
        activate_msg += "激活优惠券不成功! \n"
        return False, activate_msg

def Activate(LoginName: str, LoginPassword: str, retry_count=3):  # 默认出错会重试三次
    """
    Args:
        LoginName (str): AccountName
        LoginPassword (str): AccountPassword
        retry_count (int, optional): Retry times. Defaults to 3.

    Returns:
        str: activate_msg
    """
    success_in_progress = True
    global success_count
    activate_msg = ""
    # 网页属性
    logger.info("创建网页 ")
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless") # 不显示浏览器窗口
    chrome_options.add_argument("--no-sandbox") # 禁用沙盒提高权限
    chrome_options.add_argument("--disable-blink-features=AutomationControlled") # 自动控制模式
    chrome_options.add_argument("--disable-gpu") # 禁用GPU
    browser = webdriver.Chrome(options=chrome_options)
    browser.set_page_load_timeout(20.0)  # 设置页面加载超时时间
    wait = WebDriverWait(browser, 5)
    browser.set_window_size(1024, 768)
    # 打开网页
    if success_in_progress:
        success_in_progress, activate_msg = OpenWebSite(browser, activate_msg)
        if not success_in_progress and retry_count > 0:
            browser.quit()  # 关闭浏览器
            return Activate(LoginName, LoginPassword, retry_count - 1)
    sleep(1)
    current_url = browser.current_url
    logger.debug("当前浏览器地址: {}".format(current_url))
    if not current_url.startswith("https://passport.jlc.com/login"):
        browser.get("https://passport.jlc.com/login")
    elif current_url.startswith("https://passport.jlc.com/login"):
        # logger.info("需要登录，开始登录 ")
        # # 寻找登录界面
        if success_in_progress:
            success_in_progress, activate_msg = FindSignPage(wait, activate_msg)
            if not success_in_progress and retry_count > 0:
                browser.quit()
                return Activate(LoginName, LoginPassword, retry_count - 1)

    # 输入账号密码
    if success_in_progress:
        success_in_progress, activate_msg = EnterAccount(browser, wait, LoginName, LoginPassword, activate_msg)
        if not success_in_progress and retry_count > 0:
            browser.quit()
            return Activate(LoginName, LoginPassword, retry_count - 1)

    # 滑动验证并登录
    if success_in_progress:
        success_in_progress, activate_msg = SlideToLogin(browser, wait, activate_msg)
        if not success_in_progress and retry_count > 0:
            browser.quit()
            return Activate(LoginName, LoginPassword, retry_count - 1)

    sleep(1)
    current_url = browser.current_url  # 检查转跳后的页面网址
    logger.debug("当前浏览器地址: {}".format(current_url))
    if current_url.startswith("https://u.lceda.cn/account/user/coupon/activating"):
        sleep(1)
        # 查找待激活的優惠券按鈕
        if success_in_progress:
            success_in_progress, activate_msg = CheckCoupons(wait, activate_msg)
            if not success_in_progress and retry_count > 0:
                browser.quit()
                return Activate(LoginName, LoginPassword, retry_count - 1)
    else:
        # 轉跳到"https://u.lceda.cn/account/user/coupon/activating"
        # 再查找待激活的優惠券按鈕
        browser.get("https://u.lceda.cn/account/user/coupon/activating")
        sleep(1)
        if success_in_progress:
            success_in_progress, activate_msg = CheckCoupons(wait, activate_msg)
            if not success_in_progress and retry_count > 0:
                browser.quit()
                return Activate(LoginName, LoginPassword, retry_count - 1)

    # 最后不要忘了把网页关了
    try:
        browser.quit()
    except Exception as ex:
        logger.error(" {}".format(ex))
    # 激活顺利，则激活成功数+1
    if success_in_progress:
        pass
        # success_count += 1
    else:
        logger.error("激活过程出错")
    if not activate_msg:
        activate_msg = " "
    return activate_msg

if __name__ == "__main__":
    sign_contents = []
    notifications = "----------------------------------------------\n"
    if "OSHW" in os.environ and len(os.environ["OSHW"]) > 1:
        Users = eval(os.environ["OSHW"])
        for key in Users:
            name = key
            password = Users[key]
            try:
                masked_login_name = (
                    name[:3]
                    + "*" * (len(name) - len(name[:3]) - len(name[-2:]))
                    + name[-2:]
                )
                logger.info("开始激活优惠券 " + masked_login_name)
                try:
                    sign_contents.append(
                        masked_login_name + " \n" + Activate(name, password, 0)
                    )
                except Exception as ex:
                    logger.error("激活优惠券: {}".format(ex))
                    notifications += str(ex)
                    # 处理返回值为None的情况
                    sign_contents.append("Something Wrong with activation progress! \n")
                logger.info(sign_contents)
                logger.info("------------------------------------------")
                sign_contents = [item for item in sign_contents if item is not None]
                notifications += (
                    " ".join(sign_contents)
                    + "----------------------------------------------\n"
                )
                sign_contents = []
            except Exception as ex:
                logger.error("主程序运行错误:{}".format(ex))
                notifications += str(ex)
                traceback.print_exc()
    else:
        notifications += '“OSHW”环境变量不存在，请添加名为OSHW的环境变量, 值为{"手机号1": "密码1","手机号2": "密码2", "手机号n": "密码n"}!'
        logger.info(
            '“OSHW”环境变量不存在，请添加名为OSHW的环境变量, 值为{"手机号1": "密码1","手机号2": "密码2", "手机号n": "密码n"}!'
        )

    if ENABLE_PushNnotify:
        try:
            title = "立创优惠券激活成功" + str(success_count) + "个优惠券"
            send(title, notifications)
        except Exception:
            logger.info("再次尝试推送")
            try:
                sleep(1)
                send(title, notifications)
            except Exception as ex:
                logger.error("推送失败!:{}".format(ex))
                logger.info("再次尝试推送")
    else:
        logger.info("推送未开启")
    logger.info("激活结束 ")
