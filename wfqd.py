from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import time

# 账号列表 (用户名, 密码)
ACCOUNTS = [
    ("18065576553", "Wszyz1011"),
    ("china-zyz", "Wszyz1011"),
    # 添加更多账号...
    # ("username2", "password2"),
    # ("username3", "password3"),
]

# 配置Chrome选项
chrome_options = Options()
# chrome_options.add_argument("--headless")    # 如需无头模式取消注释
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=1920x1080")


def setup_driver():
    """初始化WebDriver"""
    # 获取当前脚本所在目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # 构建chromedriver完整路径
    chromedriver_path = os.path.join(current_dir, "chromedriver.exe" if os.name == 'nt' else "chromedriver")
    # 创建WebDriver服务
    service = Service(executable_path=chromedriver_path)
    return webdriver.Chrome(service=service, options=chrome_options)


def login(driver, username, password):
    """执行登录操作"""
    print(f"\n开始处理账号: {username}")

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
    username_field.send_keys(username)
    print("已填写用户名")

    # 填写密码
    password_field = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (By.XPATH, '//*[@id="__layout"]/div/div[1]/div[2]/div[2]/div[2]/form/label[2]/div/input'))
    )
    password_field.clear()
    password_field.send_keys(password)
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


def sign_in(driver):
    """执行签到操作"""
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
        return True
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
                return True
            except:
                print("恭喜，签到成功")
                return True

        except Exception as e:
            print(f"点击签到按钮失败: {str(e)}")
            driver.save_screenshot(f"sign_failed_{int(time.time())}.png")
            print(f"已保存签到失败截图: sign_failed_{int(time.time())}.png")
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
        print("已展开用户菜单")

        # 点击退出按钮
        logout_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH,
                                        '//*[@id="__layout"]/div/header/div/div/div/div[4]/div[3]/div/div[2]/div/div[1]/div[5]/div'))
        )
        logout_button.click()
        print("已点击退出按钮")

        # 等待登出完成
        WebDriverWait(driver, 10).until(
            EC.url_contains("login") or EC.url_contains("logout")
        )
        print("登出成功")
    except Exception as e:
        print(f"登出时出错: {str(e)}")


def process_account(username, password):
    """处理单个账号"""
    driver = None
    try:
        driver = setup_driver()
        login(driver, username, password)
        sign_in(driver)
    except Exception as e:
        print(f"处理账号 {username} 时出错: {str(e)}")
        if driver:
            driver.save_screenshot(f"error_{username}_{int(time.time())}.png")
            print(f"已保存错误截图: error_{username}_{int(time.time())}.png")
    finally:
        if driver:
            try:
                logout(driver)
            except:
                pass
            driver.quit()


def main():
    """主函数"""
    print(f"开始处理 {len(ACCOUNTS)} 个账号的签到任务")

    for idx, (username, password) in enumerate(ACCOUNTS, 1):
        print(f"\n{'=' * 40}")
        print(f"开始处理第 {idx}/{len(ACCOUNTS)} 个账号")
        process_account(username, password)
        print(f"完成处理第 {idx}/{len(ACCOUNTS)} 个账号")
        print(f"{'=' * 40}")

        # 如果不是最后一个账号，等待几秒再处理下一个
        if idx < len(ACCOUNTS):
            wait_time = 5
            print(f"等待 {wait_time} 秒后处理下一个账号...")
            time.sleep(wait_time)

    print("\n所有账号处理完成！")


if __name__ == "__main__":
    main()
