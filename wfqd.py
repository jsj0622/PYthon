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
    username_field.send_keys("18065576553")
    print("已填写用户名")

    # 填写密码
    password_field = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (By.XPATH, '//*[@id="__layout"]/div/div[1]/div[2]/div[2]/div[2]/form/label[2]/div/input'))
    )
    password_field.clear()
    password_field.send_keys("Wszyz1011")
    print("已填写密码")

    # 点击登录按钮
    login_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="login-btn"]'))
    )
    login_button.click()
    print("已点击登录按钮")

    # 等待登录完成
    WebDriverWait(driver, 15).until(
        lambda d: "dashboard" in d.current_url.lower() or
                  "welcome" in d.page_source.lower() or
                  "我的主页" in d.page_source
    )
    print("登录成功！")

    # 最大化浏览器窗口
    driver.maximize_window()
    print("浏览器已最大化")

    # 点击用户菜单展开按钮
    user_menu_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable(
            (By.XPATH, '//*[@id="__layout"]/div/header/div/div/div/div[4]/div[3]/div/div[1]/div'))
    )
    user_menu_button.click()
    print("已展开用户菜单")

    # 检查是否已签到
    try:
        # 等待最多3秒看是否出现"已签到"文本
        WebDriverWait(driver, 3).until(
            EC.text_to_be_present_in_element((By.XPATH, "//*[contains(text(), '已连续签到')]"), "已连续签到")
        )
        print("检测到'已连续签到'，无需重复签到")
    except:
        print("未检测到'已连续签到'文本，尝试签到")

        # 点击签到按钮
        try:
            sign_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH,
                                            '//*[@id="__layout"]/div/header/div/div/div/div[4]/div[3]/div/div[2]/div/div[1]/div[4]/div/button'))
            )
            sign_button.click()
            print("已点击签到按钮")

            # 等待签到完成，检查是否出现签到成功提示
            try:
                WebDriverWait(driver, 5).until(
                    EC.text_to_be_present_in_element(
                        (By.XPATH, "//*[contains(text(), '签到成功') or contains(text(), '已签到')]"), "签到")
                )
                print("签到成功")
            except:
                print("恭喜，签到成功")

        except Exception as e:
            print(f"点击签到按钮失败: {str(e)}")
            driver.save_screenshot("sign_failed.png")
            print("已保存签到失败截图: sign_failed.png")

            # 无论是否签到，最终都关闭浏览器
    print("操作完成，准备关闭浏览器")
    driver.quit()

except Exception as e:
    print(f"发生错误: {str(e)}")
    if 'driver' in locals():
        driver.save_screenshot("error.png")
        print("已保存错误截图: error.png")
    raise e  # 重新抛出异常以便调试

finally:
    if 'driver' in locals():
        driver.quit()
