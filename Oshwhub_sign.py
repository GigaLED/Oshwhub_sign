import os
import re
import sys
import traceback
import datetime
import subprocess
from dateutil.relativedelta import relativedelta
from time import sleep
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from loguru import logger

# 检查命令行参数中是否有'--debug'
DEBUG = '--debug' in sys.argv

ENABLE_PushNnotify = True  # 消息推送开关
ENABLE_WeekReward = True  # 七日奖励领取开关
ENABLE_MonthReward = True  # 月度奖励领取开关，只有每月最后一天会运行，其他时间只会检测签到天数
ENABLE_PushPoints = True  # 推送积分数开关
EMABLE_CouponActivation = True  # 优惠券激活开关

DELAY: int = 2  # 延迟时间,单位:秒,默认2秒,可自行调整

if ENABLE_PushNnotify:
    try:
        from notify import send
    except ModuleNotFoundError as ex:
        logger.info("notify 模块未找到，跳过推送! ")
        ENABLE_PushNnotify = False

success_count = 0
Coupon_Exist = False


def OpenWebSite(browser: webdriver.Chrome, sign_msg: str):
    """Open the WebSite

    Args:
        browser (webdriver.Chrome): A Chrome browser instance
        sign_msg (str): sign_msg

    Returns:
        bool: Running successfully or not
        str: sign_msg
    """
    try:
        browser.get("https://oshwhub.com/sign_in")
        return True, sign_msg
    except TimeoutException as ex:
        logger.error("页面加载超时!: {}".format(ex))
        sign_msg += "页面加载超时! \n"
        return False, sign_msg
    except WebDriverException as ex:
        logger.error("页面崩溃!: {}".format(ex))
        sign_msg += "页面崩溃! \n"
        return False, sign_msg


def FindSignPage(browser: webdriver.Chrome, wait: WebDriverWait, sign_msg: str):
    """Find the sign page witch use username and password

    Args:
        wait (WebDriverWait): A WebDriverWait object to wait for the browser to complete an operation.
        sign_msg (str): sign_msg

    Returns:
        bool: Running successfully or not
        str: sign_msg
    """
    logger.info("需要登录，开始登录 ")
    # 寻找登录界面
    try:
        logger.info("寻找登录界面 ")
        PasswordEntryPage = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#__layout > div > div > div > main > div > div > div:nth-child(2) > div:nth-child(1) > ul > li:nth-child(2)")))
        # PasswordEntryPage.click()
        actions = ActionChains(browser)
        actions.move_to_element(PasswordEntryPage).click().perform()
        return True, sign_msg
    except Exception as ex:
        logger.error("无法登录:未找到密码登陆界面!: {}".format(ex))
        sign_msg += "无法登录:未找到密码登陆界面! \n"
        return False, sign_msg


def EnterAccount(browser: webdriver.Chrome, wait: WebDriverWait, LoginName: str, LoginPassword: str, sign_msg: str):
    """Enter account name and password to input box

    Args:
        browser (webdriver.Chrome): A Chrome browser instance
        wait (WebDriverWait): A WebDriverWait object to wait for the browser to complete an operation.
        LoginName (str): _description_
        LoginPassword (str): _description_
        sign_msg (str): sign_msg

    Returns:
        bool: Running successfully or not
        str: sign_msg
    """
    try:
        logger.info("输入账号密码 ")
        username_input = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#__layout > div > div > div > main > div > div > div:nth-child(2) > div:nth-child(1) > div > div:nth-child(2) > div > form > div:nth-child(1) > div > div:nth-child(1) > div > input")))
        username_input.clear()
        username_input.send_keys(LoginName)
        password_input = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#__layout > div > div > div > main > div > div > div:nth-child(2) > div:nth-child(1) > div > div:nth-child(2) > div > form > div:nth-child(2) > div > div:nth-child(1) > div > input")))
        password_input.clear()
        password_input.send_keys(LoginPassword)
        return True, sign_msg
    except Exception as ex:
        logger.error("无法登录:账号密码输入未成功!: {}".format(ex))
        sign_msg += "无法登录:账号密码输入未成功! \n"
        browser.quit()
        return False, sign_msg


def SlideToLogin(browser: webdriver.Chrome, wait: WebDriverWait, sign_msg: str):
    """Control the slidebar rto login

    Args:
        browser (webdriver.Chrome): A Chrome browser instance
        wait (WebDriverWait): A WebDriverWait object to wait for the browser to complete an operation.
        sign_msg (str): sign_msg

    Returns:
        bool: Running successfully or not
        str: sign_msg
    """
    try:
        logger.info("滑动验证并登录 ")
        slider = wait.until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="nc_1_n1z"]')))
        ActionChains(browser).drag_and_drop_by_offset(slider, 400, 0).perform()
        sleep(DELAY)
        confirm_button = wait.until(
            EC.presence_of_element_located((By.XPATH, """//*[@id="__layout"]/div/div/div/main/div/div/div[2]/div[1]/div/div[2]/div/button""")))
        # confirm_button.click()
        actions = ActionChains(browser)
        actions.move_to_element(confirm_button).click().perform()
        # 激活
        sleep(2)
        return True, sign_msg
    except Exception as ex:
        logger.error("无法登录:滑动验证或登录不成功!: {}".format(ex))
        sign_msg += "无法登录:滑动验证或登录不成功! \n"
        return False, sign_msg


def DailyAttendance(browser: webdriver.Chrome, wait: WebDriverWait, sign_msg: str):
    """Daily Attendance

    Args:
        browser (webdriver.Chrome): A Chrome browser instance
        wait (WebDriverWait): A WebDriverWait object to wait for the browser to complete an operation.
        sign_msg (str): sign_msg

    Returns:
        bool: Running successfully or not
        str: sign_msg
    """
    try:
        logger.debug("当前浏览器地址: {}".format(browser.current_url))
        logger.info("每日签到: ")
        sign_msg += "每日签到: "
        sleep(DELAY)

        sign_in_button = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.XPATH, '/html/body/div[2]/div/div[1]/div[1]/div/div[1]/div[2]/div[1]/div[1]/span[2]'))
        )
        sleep(1)
        sign_in_button_status = sign_in_button.text
        if "立即签到" in sign_in_button_status:
            actions = ActionChains(browser)
            actions.move_to_element(sign_in_button).click().perform()
            # sign_in_button.click()
            logger.info("签到成功 ")
            sign_msg += "签到成功 \n"
        elif "已签到" in sign_in_button_status:
            logger.warning("重复签到! ")
            sign_msg += "重复签到! \n"
        else:
            logger.error("签到失败! ")
            sign_msg += "签到失败! \n"
        return True, sign_msg
    except Exception as ex:
        logger.error("签到错误!: {}".format(ex))
        sign_msg += "签到错误! \n"
        return False, sign_msg


def WeekAttendance(browser: webdriver.Chrome, wait: WebDriverWait, sign_msg: str):
    """Weekly Attendance

    Args:
        browser (webdriver.Chrome): A Chrome browser instance
        wait (WebDriverWait): A WebDriverWait object to wait for the browser to complete an operation.
        sign_msg (str): sign_msg

    Returns:
        bool: Running successfully or not
        str: sign_msg
    """
    today = datetime.date.today()
    # 七日签到 需要开启ENABLE_WeekReward
    global ENABLE_WeekReward, Coupon_Exist
    if ENABLE_WeekReward:
        logger.info("七日奖励 ")
        sign_msg += "七日奖励: "
        if today.weekday() == 6:
            try:  # 执行网页刷新
                browser.refresh()
                logger.info("七日签到网页刷新成功")
                try:
                    sleep(DELAY)
                    week_reword_button = wait.until(
                        EC.presence_of_element_located((  # 七日签到按钮
                            By.XPATH,
                            "/html/body/div[2]/div/div[1]/div[1]/div/div[1]/div[1]/div[2]/div[1]")))  # 七日签到按钮
                    sleep(1)
                    week_reword_status = week_reword_button.get_attribute('title')
                    # to-do
                    if ("不可" in week_reword_status):
                        logger.warning("不可领取")
                        sign_msg += "不可领取 \n"
                    else:
                        try:  # 获取奖励内容
                            logger.debug("正在点击七日奖励领取按钮 ")
                            actions = ActionChains(browser)
                            actions.move_to_element(week_reword_button).click().perform()
                            # week_reword_button.click()
                            logger.info("领取七日奖励成功 ")
                            sign_msg += "领取奖励成功 \n"
                            sleep(DELAY)
                        except TimeoutException as ex:
                            logger.error("获取七日奖励加载超时!: {}".format(ex))
                            sign_msg += "获取七日奖励加载超时! \n"
                        except Exception as ex:
                            logger.error("七日奖励可以领取但领取错误!: {}".format(ex))
                            sign_msg += "奖励可以领取但领取错误! \n"
                    return True, sign_msg
                except Exception as ex:
                    logger.error("七日奖励异常!: {}".format(ex))
                    sign_msg += "七日奖励异常! \n"
                    return False, sign_msg
            except Exception as ex:
                logger.error("七日签到网页刷新失败: {}".format(ex))
                sign_msg += "七日签到网页刷新失败! \n"
                return False, sign_msg
        else:
            logger.info("未到周日! ")
            sign_msg += "未到周日! \n"
            return True, sign_msg
    else:
        logger.info("跳过七日奖励检测! ")
        # sign_msg += "跳过七日奖励检测! \n"
        return True, sign_msg


def MonthAttendance(browser: webdriver.Chrome, wait: WebDriverWait, sign_msg: str):
    """Monthly Attendance

    Args:
        browser (webdriver.Chrome): A Chrome browser instance
        wait (WebDriverWait): A WebDriverWait object to wait for the browser to complete an operation.
        sign_msg (str): sign_msg

    Returns:
        bool: Running successfully or not
        str: sign_msg
    """
    today = datetime.date.today()
    last_day_of_month = (
        today.replace(day=1) + relativedelta(months=1) - datetime.timedelta(days=1)
    )
    global ENABLE_MonthReward, Coupon_Exist
    if ENABLE_MonthReward:
        logger.info("月度奖励 ")
        sign_msg += "月度奖励: "
        if today == last_day_of_month:
            try:  # 执行网页刷新
                browser.refresh()
                logger.info("月度签到网页刷新成功")
                try:
                    sleep(DELAY)
                    month_reword_button = wait.until(
                        EC.presence_of_element_located((  # 月度签到按钮
                            By.XPATH,
                            "/html/body/div[2]/div/div[1]/div[1]/div/div[1]/div[1]/div[2]/div[2]")))  # 月度签到按钮
                    sleep(1)
                    month_reword_status = month_reword_button.get_attribute('title')
                    month_signdays = wait.until(
                        EC.presence_of_element_located((  # 月度签到天数
                            By.XPATH,
                            "/html/body/div[2]/div/div[1]/div[1]/div/div[1]/div[2]/div[2]/div[1]/div[1]/span")))  # 月度签到天数元素
                    numbers = re.findall(r'\d+', month_signdays.text)
                    extracted_numbers = [int(num) for num in numbers]
                    logger.debug("本月已签到{}天".format(extracted_numbers))

                    if ("不可" in month_reword_status):
                        logger.warning("不可领取")
                        sign_msg += "不可领取 \n"
                    else:
                        try:  # 获取奖励内容
                            logger.debug("正在点击月度奖励领取按钮 ")
                            actions = ActionChains(browser)
                            actions.move_to_element(month_reword_button).click().perform()
                            # month_reword_button.click()
                            logger.info("领取月度奖励成功 ")
                            sign_msg += "领取奖励成功 \n"
                            sleep(DELAY)
                        except TimeoutException as ex:
                            logger.error("获取月度奖励加载超时!: {}".format(ex))
                            sign_msg += "获取月度奖励加载超时! \n"
                        except Exception as ex:
                            logger.error("月度奖励可以领取但领取错误!: {}".format(ex))
                            sign_msg += "奖励可以领取但领取错误! \n"
                    return True, sign_msg
                except Exception as ex:
                    logger.error("月度奖励异常!: {}".format(ex))
                    sign_msg += "月度奖励异常! \n"
                    return False, sign_msg
            except Exception as ex:
                logger.error("月度签到网页刷新失败: {}".format(ex))
                return False, sign_msg
        else:
            month_signdays = wait.until(
                EC.presence_of_element_located((  # 月度签到天数
                    By.XPATH,
                    "/html/body/div[2]/div/div[1]/div[1]/div/div[1]/div[2]/div[2]/div[1]/div[1]/span")))  # 月度签到天数元素
            numbers = re.findall(r'\d+', month_signdays.text)
            extracted_numbers = [int(num) for num in numbers]
            logger.info("本月已签到{}天".format(extracted_numbers))
            logger.info("未到月末! ")
            sign_msg += "未到月末! \n"
            return True, sign_msg
    else:
        logger.info("跳过月度奖励获取! ")
        # sign_msg += "跳过月度奖励获取! \n"
        return True, sign_msg


def CheckPoints(browser: webdriver.Chrome, wait: WebDriverWait, sign_msg: str):
    """Check Total Points

    Args:
        browser (webdriver.Chrome): A Chrome browser instance
        wait (WebDriverWait): A WebDriverWait object to wait for the browser to complete an operation.
        sign_msg (str): sign_msg

    Returns:
        bool: Running successfully or not
        str: sign_msg
    """
    # 查询积分 需要开启ENABLE_PushPoints
    global ENABLE_PushPoints
    if ENABLE_PushPoints:
        try:
            # 执行网页刷新
            browser.refresh()
            logger.info("积分查询网页刷新成功")
        except Exception as ex:
            logger.error("积分查询网页刷新失败: {}".format(ex))
            sign_msg += "积分查询网页刷新失败! \n"
            return False, sign_msg

        try:
            sleep(1)
            data_totalpoints = wait.until(
                EC.presence_of_element_located((
                    By.XPATH,
                    "/html/body/div[2]/div/div[1]/div[1]/div/div[1]/div[1]/div[1]/div[2]/span[1]")))
            my_points = data_totalpoints.text
            logger.info("我的积分:{}".format(my_points))
            # logger.info("我的积分: " + my_points + " ")
            sign_msg += "我的积分:" + my_points + " \n"
        except Exception as ex:
            logger.error("积分查询错误!: {}".format(ex))
            sign_msg += "积分查询错误! \n"
            return False, sign_msg

        try:
            expire_points_info_ele = wait.until(
                EC.presence_of_element_located((  # 积分过期时间
                    By.XPATH,
                    "/html/body/div[2]/div/div[1]/div[1]/div/div[1]/div[1]/div[1]/div[1]/span[2]")))
            expire_points_info = expire_points_info_ele.text
            logger.info("{}".format(expire_points_info))
            sign_msg += "{}".format(expire_points_info) + " \n"
        except Exception:
            logger.info("没有积分会过期")

        return True, sign_msg
    else:
        logger.info("跳过积分推送! ")
        # sign_msg += "跳过积分推送! \n"
        return True, sign_msg


def sign(LoginName: str, LoginPassword: str, retry_count=3):  # 默认出错会重试三次
    """
    Args:
        LoginName (str): AccountName
        LoginPassword (str): AccountPassword
        retry_count (int, optional): Retry times. Defaults to 3.

    Returns:
        str: sign_msg
    """
    success_in_progress = True
    global success_count
    sign_msg = ""
    # 网页属性
    logger.info("创建网页 ")
    chrome_options = webdriver.ChromeOptions()
    if not DEBUG:
        chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--incognito')  # 无痕隐身模式
    chrome_options.add_argument("--enable-unsafe-swiftshader")
    chrome_options.add_argument("disable-cache")  # 禁用缓存
    chrome_options.add_argument('disable-infobars')  # 禁用浏览器正在受到自动测试软件的控制提示
    chrome_options.add_argument('log-level=3')  # INFO = 0 WARNING = 1 LOG_ERROR = 2 LOG_FATAL = 3 default is 0

    try:
        browser = webdriver.Chrome(options=chrome_options)
        browser.set_page_load_timeout(20.0)  # 设置页面加载超时时间
        wait = WebDriverWait(browser, 10)
        browser.set_window_size(1024, 768)

        # 打开网页
        if success_in_progress:
            success_in_progress, sign_msg = OpenWebSite(browser, sign_msg)
            if not success_in_progress and retry_count > 0:
                browser.quit()  # 关闭浏览器
                return sign(LoginName, LoginPassword, retry_count - 1)

        # 寻找登录界面
        if success_in_progress:
            success_in_progress, sign_msg = FindSignPage(browser, wait, sign_msg)
            if not success_in_progress and retry_count > 0:
                browser.quit()
                return sign(LoginName, LoginPassword, retry_count - 1)

        # 输入账号密码
        if success_in_progress:
            success_in_progress, sign_msg = EnterAccount(browser, wait, LoginName, LoginPassword, sign_msg)
            if not success_in_progress and retry_count > 0:
                browser.quit()
                return sign(LoginName, LoginPassword, retry_count - 1)

        # 滑动验证并登录
        if success_in_progress:
            success_in_progress, sign_msg = SlideToLogin(browser, wait, sign_msg)
            if not success_in_progress and retry_count > 0:
                browser.quit()
                return sign(LoginName, LoginPassword, retry_count - 1)

        # 每日签到
        if success_in_progress:
            success_in_progress, sign_msg = DailyAttendance(browser, wait, sign_msg)
            if not success_in_progress and retry_count > 0:
                browser.quit()
                return sign(LoginName, LoginPassword, retry_count - 1)

        # 每周签到
        if success_in_progress:
            success_in_progress, sign_msg = WeekAttendance(browser, wait, sign_msg)
            if not success_in_progress and retry_count > 0:
                browser.quit()
                return sign(LoginName, LoginPassword, retry_count - 1)

        # 每月签到
        if success_in_progress:
            success_in_progress, sign_msg = MonthAttendance(browser, wait, sign_msg)
            if not success_in_progress and retry_count > 0:
                browser.quit()
                return sign(LoginName, LoginPassword, retry_count - 1)

        # 查询积分
        if success_in_progress:
            success_in_progress, sign_msg = CheckPoints(browser, wait, sign_msg)
            if not success_in_progress and retry_count > 0:
                browser.quit()
                return sign(LoginName, LoginPassword, retry_count - 1)

    finally:
        browser.quit()
        logger.info("关闭浏览器")

        # 签到顺利，则签到成功数+1
        if success_in_progress:
            success_count += 1
        else:
            logger.error("签到过程出错")
        return sign_msg

# 主程序
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
                logger.info("开始签到 " + masked_login_name)
                try:
                    sign_contents.append(
                        masked_login_name + " \n" + sign(name, password, 3)
                    )
                except Exception as ex:
                    logger.error("签到出错: {}".format(ex))
                    notifications += str(ex)
                    # 处理返回值为None的情况
                    sign_contents.append("Something Wrong with sign progress! \n")
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
    if ENABLE_PushNnotify and "notify" in sys.modules:
        try:
            title = "立创签到成功" + str(success_count) + "个账号"
            send(title, notifications)
        except Exception:
            logger.error("推送失败!:{}".format(ex))
    else:
        logger.info("\n" + notifications)

    logger.info("签到结束 ")
    logger.debug(f"签到记录：\n {notifications}")

    # 如果奖励里有优惠券，则启动激活优惠券程序
    if EMABLE_CouponActivation and Coupon_Exist:
        # 定义要运行的脚本的路径
        script_path = "ActivateCoupons.py"
        # 使用 subprocess 模块运行脚本的 main 函数
        # 使用 os.path.exists() 函数检查文件是否存在
        if os.path.exists(script_path):
            # 如果文件存在，运行脚本
            subprocess.run(["python", script_path, "main"])
        else:
            # 如果文件不存在，打印错误消息
            print(f"File {script_path} does not exist.")
        pass
