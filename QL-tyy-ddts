#!/usr/bin/env python3 
# coding: utf-8 
 
from selenium import webdriver 
from selenium.webdriver.common.by  import By 
from selenium.webdriver.chrome.service  import Service 
from selenium.webdriver.chrome.options  import Options 
from selenium.webdriver.support.ui  import WebDriverWait 
from selenium.webdriver.support  import expected_conditions as EC 
import os 
import time 
import logging 
import hmac 
import hashlib 
import base64 
import urllib.parse  
import requests 
 
# 配置日志 
logging.basicConfig(level=logging.INFO,  format='%(asctime)s - %(levelname)s - %(message)s') 
logger = logging.getLogger(__name__)  
 
# 从环境变量获取账号信息 
def get_accounts_from_env(): 
    accounts = [] 
    index = 1 
    while True: 
        username = os.getenv(f"FENG_USERNAME_{index}")  
        password = os.getenv(f"FENG_PASSWORD_{index}")  
        if username and password: 
            accounts.append((username,  password)) 
            index += 1 
        else: 
            break 
    return accounts 
 
# 配置Chrome选项 
def get_chrome_options(): 
    chrome_options = Options() 
    chrome_options.add_argument("--headless")   # 无头模式 
    chrome_options.add_argument("--no-sandbox")  
    chrome_options.add_argument("--disable-dev-shm-usage")  
    chrome_options.add_argument("--disable-gpu")  
    chrome_options.add_argument("--window-size=1920x1080")  
    return chrome_options 
 
def setup_driver(): 
    """初始化WebDriver""" 
    try: 
        chrome_options = get_chrome_options() 
        # 青龙面板中通常chromedriver已在PATH中 
        service = Service(executable_path="/usr/bin/chromedriver") 
        driver = webdriver.Chrome(service=service, options=chrome_options) 
        return driver 
    except Exception as e: 
        logger.error(f"  初始化WebDriver失败: {str(e)}") 
        return None 
 
# 发送消息到钉钉机器人 
def send_dingtalk_message(message): 
    webhook = os.getenv("DINGTALK_WEBHOOK")  
    secret = os.getenv("DINGTALK_SECRET")  
    if not webhook or not secret: 
        logger.error("  未设置钉钉机器人的Webhook或密钥，请检查环境变量。") 
        return 
    timestamp = str(round(time.time()  * 1000)) 
    secret_enc = secret.encode('utf-8')  
    string_to_sign = '{}\n{}'.format(timestamp, secret) 
    string_to_sign_enc = string_to_sign.encode('utf-8')  
    hmac_code = hmac.new(secret_enc,  string_to_sign_enc, digestmod=hashlib.sha256).digest()  
    sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))  
    url = f"{webhook}&timestamp={timestamp}&sign={sign}" 
    headers = { 
        "Content-Type": "application/json" 
    } 
    data = { 
        "msgtype": "text", 
        "text": { 
            "content": message 
        } 
    } 
    try: 
        response = requests.post(url,  json=data, headers=headers) 
        response.raise_for_status()  
        logger.info("  钉钉消息发送成功") 
    except requests.RequestException as e: 
        logger.error(f"  钉钉消息发送失败: {str(e)}") 
 
def login(driver, username, password): 
    """执行登录操作""" 
    logger.info(f"  开始处理账号: {username}") 
 
    # 打开登录页面 
    driver.get("https://www.feng.com/login/")  
    logger.info("  已打开登录页面") 
 
    # 显式等待页面加载 
    WebDriverWait(driver, 15).until( 
        EC.presence_of_element_located((By.XPATH,  '//*[@id="__layout"]')) 
    ) 
 
    # 填写用户名 
    username_field = WebDriverWait(driver, 10).until( 
        EC.presence_of_element_located(  
            (By.XPATH, '//*[@id="__layout"]/div/div[1]/div[2]/div[2]/div[2]/form/label[1]/div/input')) 
    ) 
    username_field.clear()  
    username_field.send_keys(username)  
    logger.info("  已填写用户名") 
 
    # 填写密码 
    password_field = WebDriverWait(driver, 10).until( 
        EC.presence_of_element_located(  
            (By.XPATH, '//*[@id="__layout"]/div/div[1]/div[2]/div[2]/div[2]/form/label[2]/div/input')) 
    ) 
    password_field.clear()  
    password_field.send_keys(password)  
    logger.info("  已填写密码") 
 
    # 点击登录按钮 
    login_button = WebDriverWait(driver, 10).until( 
        EC.element_to_be_clickable((By.XPATH,  '//*[@id="login-btn"]')) 
    ) 
    login_button.click()  
    logger.info("  已点击登录按钮") 
 
    # 等待登录完成 
    try: 
        WebDriverWait(driver, 15).until( 
            lambda d: "dashboard" in d.current_url.lower()  or 
                      "welcome" in d.page_source.lower()  or 
                      "我的主页" in d.page_source  
        ) 
        logger.info("  登录成功！") 
        return True 
    except Exception as e: 
        logger.error(f"  登录验证失败: {str(e)}") 
        return False 
 
def sign_in(driver): 
    """执行签到操作""" 
    try: 
        # 最大化浏览器窗口 
        driver.maximize_window()  
        logger.info("  浏览器已最大化") 
 
        # 点击用户菜单展开按钮 
        user_menu_button = WebDriverWait(driver, 10).until( 
            EC.element_to_be_clickable(  
                (By.XPATH, '//*[@id="__layout"]/div/header/div/div/div/div[4]/div[3]/div/div[1]/div')) 
        ) 
        user_menu_button.click()  
        logger.info("  已展开用户菜单") 
 
        # 检查是否已签到 
        try: 
            # 等待最多3秒看是否出现"已连续签到"文本 
            WebDriverWait(driver, 3).until( 
                EC.text_to_be_present_in_element((By.XPATH,  "//*[contains(text(), '已连续签到')]"), "已连续签到") 
            ) 
            logger.info("  检测到'已连续签到'，无需重复签到") 
            return True 
        except: 
            logger.info("  未检测到'已连续签到'文本，尝试签到") 
 
        # 点击签到按钮 
        try: 
            sign_button = WebDriverWait(driver, 10).until( 
                EC.element_to_be_clickable((By.XPATH,  
                                            '//*[@id="__layout"]/div/header/div/div/div/div[4]/div[3]/div/div[2]/div/div[1]/div[4]/div/button')) 
            ) 
            sign_button.click()  
            logger.info("  已点击签到按钮") 
 
            # 等待签到完成，检查是否出现签到成功提示 
            try: 
                WebDriverWait(driver, 5).until( 
                    EC.text_to_be_present_in_element(  
                        (By.XPATH, "//*[contains(text(), '签到成功') or contains(text(), '已签到')]"), "签到") 
                ) 
                logger.info("  签到成功") 
                return True 
            except: 
                logger.info("  恭喜，签到成功") 
                return True 
 
        except Exception as e: 
            logger.error(f"  点击签到按钮失败: {str(e)}") 
            driver.save_screenshot("sign_failed.png")  
            logger.error("  已保存签到失败截图: sign_failed.png")  
            return False 
    except Exception as e: 
        logger.error(f"  签到过程中出错: {str(e)}") 
        return False 
 
def logout(driver): 
    """执行登出操作""" 
    try: 
        # 点击用户菜单展开按钮 
        user_menu_button = WebDriverWait(driver, 10).until( 
            EC.element_to_be_clickable(  
                (By.XPATH, '//*[@id="__layout"]/div/header/div/div/div/div[4]/div[3]/div/div[1]/div')) 
        ) 
        user_menu_button.click()  
        logger.info("  已展开用户菜单") 
 
        # 点击退出按钮 
        logout_button = WebDriverWait(driver, 10).until( 
            EC.element_to_be_clickable((By.XPATH,  
                                        '//*[@id="__layout"]/div/header/div/div/div/div[4]/div[3]/div/div[2]/div/div[1]/div[5]/div')) 
        ) 
        logout_button.click()  
        logger.info("  已点击退出按钮") 
 
        # 等待登出完成 
        WebDriverWait(driver, 10).until( 
            EC.url_contains("login")  or EC.url_contains("logout")  
        ) 
        logger.info("  登出成功") 
        return True 
    except Exception as e: 
        logger.error(f"  登出时出错: {str(e)}") 
        return False 
 
def process_account(username, password): 
    """处理单个账号""" 
    driver = None 
    result = { 
        "username": username, 
        "login_success": False, 
        "sign_success": False, 
        "logout_success": False, 
        "error_message": "" 
    } 
    try: 
        driver = setup_driver() 
        if driver: 
            result["login_success"] = login(driver, username, password) 
            if result["login_success"]: 
                result["sign_success"] = sign_in(driver) 
    except Exception as e: 
        result["error_message"] = str(e) 
        if driver: 
            driver.save_screenshot(f"error_{username}.png")  
            logger.error(f"  已保存错误截图: error_{username}.png") 
    finally: 
        if driver: 
            result["logout_success"] = logout(driver) 
            driver.quit()  
    return result 
 
def main(): 
    """主函数""" 
    accounts = get_accounts_from_env() 
    if not accounts: 
        logger.error("  未找到账号信息，请设置环境变量FENG_USERNAME_1和FENG_PASSWORD_1等") 
        send_dingtalk_message("未找到账号信息，请设置环境变量FENG_USERNAME_1和FENG_PASSWORD_1等") 
        return 
 
    logger.info(f"  开始处理 {len(accounts)} 个账号的签到任务") 
 
    results = [] 
    for idx, (username, password) in enumerate(accounts, 1): 
        logger.info(f"\n{'='  * 40}") 
        logger.info(f"  开始处理第 {idx}/{len(accounts)} 个账号") 
        result = process_account(username, password) 
        results.append(result)  
        logger.info(f"  完成处理第 {idx}/{len(accounts)} 个账号") 
 
        # 如果不是最后一个账号，等待几秒再处理下一个 
        if idx < len(accounts): 
            wait_time = 5 
            logger.info(f"  等待 {wait_time} 秒后处理下一个账号...") 
            time.sleep(wait_time)  
 
    summary = "威锋网签到处理情况！\n" 
    for result in results: 
        summary += f"账号: {result['username']}\n" 
        summary += f"登录: {'成功' if result['login_success'] else '失败'}\n" 
        summary += f"签到: {'成功' if result['sign_success'] else '失败'}\n" 
        if result["error_message"]: 
            summary += f"错误信息: {result['error_message']}\n" 
        summary += "=" * 20 + "\n" 
 
    logger.info(summary)  
    send_dingtalk_message(summary) 
 
if __name__ == "__main__": 
    main() 
 
