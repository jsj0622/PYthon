from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import time

# 配置Chrome选项
chrome_options = Options()
# chrome_options.add_argument("--headless")   # 如需无头模式取消注释
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=1920x1080")

# 获取当前脚本所在目录
current_dir = os.path.dirname(os.path.abspath(__file__))

# 构建chromedriver完整路径
chromedriver_path = os.path.join(current_dir, "chromedriver.exe" if os.name == 'nt' else "chromedriver")

# 创建WebDriver服务
service = Service(executable_path=chromedriver_path)

try:
    # 初始化WebDriver
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # 打开登录页面
    driver.get("https://www.feng.com/login/")
    print("已打开登录页面")

    # 显式等待页面加载
    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="__layout"]'))
    )

    # 填写用户名
    username_field = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (By.XPATH, '//*[@id="__layout"]/div/div[1]/div[2]/div[2]/div[2]/form/label[1]/div/input'))
    )
    username_field.clear()
    username_field.send_keys("china-zyz")
    print("已填写用户名")

    # 填写密码
    password_field = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (By.XPATH, '//*[@id="__layout"]/div/div[1]/div[2]/div[2]/div[2]/form/label[2]/div/input'))
    )
    password_field.clear()
    password_field.send_keys("zyzmckkhn")
    print("已填写密码")

    # 点击登录按钮（使用你提供的XPath）
    login_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="login-btn"]'))
    )
    login_button.click()
    print("已点击登录按钮")

    # 等待登录完成（增加显式等待）
    try:
        WebDriverWait(driver, 15).until(
            lambda d: "dashboard" in d.current_url.lower() or
                      "welcome" in d.page_source.lower() or
                      "我的主页" in d.page_source  # 添加中文页面判断
        )
        print("登录成功！")
        # 登录成功后可以添加后续操作
    except Exception as e:
        print(f"登录状态检查失败: {str(e)}")
        driver.save_screenshot("login_status.png")
        print("已保存登录状态截图: login_status.png")

except Exception as e:
    print(f"发生错误: {str(e)}")
    if 'driver' in locals():
        driver.save_screenshot("error.png")
        print("已保存错误截图: error.png")
    raise e  # 重新抛出异常以便调试

finally:
    if 'driver' in locals():
        # 调试时可以注释掉下面这行，让浏览器保持打开状态
        input("按Enter键关闭浏览器...")
        driver.quit()