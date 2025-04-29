import pygetwindow as gw
import pyautogui
import screeninfo
import keyboard
import time
import pystray
from pystray import MenuItem as item
from PIL import Image
import threading
import win32con
import win32gui
import win32process
import ctypes
import os
import sys
import winreg

# 【1】修改：记录每个屏幕的窗口最小化状态
minimized_windows_per_screen = {}  # 每个屏幕对应隐藏的窗口列表
is_minimized_per_screen = {}       # 每个屏幕的最小化状态
window_states = {}  # 保存窗口最大化状态

def get_mouse_screen():
    monitors = screeninfo.get_monitors()
    x, y = pyautogui.position()
    for m in monitors:
        if m.x <= x < m.x + m.width and m.y <= m.y + m.height:
            return (m.x, m.y, m.x + m.width, m.y + m.height)
    return None

def minimize_windows_on_screen(target_screen):
    global minimized_windows_per_screen, window_states
    left, top, right, bottom = target_screen
    minimized_windows = []
    all_windows = gw.getAllWindows()
    for w in all_windows:
        if not w.visible or not w.title:
            continue
        box = w.box
        box_right = box.left + box.width
        box_bottom = box.top + box.height
        cx = (box.left + box_right) // 2
        cy = (box.top + box_bottom) // 2
        if left <= cx < right and top <= cy < bottom:
            try:
                window_states[w._hWnd] = w.isMaximized
                minimized_windows.append(w)
                force_hide_wechat(w._hWnd)
            except Exception:
                pass
    minimized_windows_per_screen[target_screen] = minimized_windows  # 存下来！

def restore_windows(target_screen):
    global minimized_windows_per_screen, window_states
    minimized_windows = minimized_windows_per_screen.get(target_screen, [])
    for w in reversed(minimized_windows):
        try:
            restore_window_and_children(w._hWnd)
        except Exception:
            pass
    time.sleep(0.2)
    for w in reversed(minimized_windows):
        try:
            hwnd = w._hWnd
            if window_states.get(hwnd):
                w.maximize()
            time.sleep(0.05)
        except Exception as e:
            print(f"将窗口置于前台时出错: {e}")
    minimized_windows_per_screen[target_screen] = []  # 清空

def on_hotkey():
    screen = get_mouse_screen()
    if not screen:
        return
    # 判断当前屏幕是否已经最小化过
    if not is_minimized_per_screen.get(screen, False):
        minimize_windows_on_screen(screen)
        is_minimized_per_screen[screen] = True
    else:
        restore_windows(screen)
        is_minimized_per_screen[screen] = False

def force_hide_wechat(hwnd):
    try:
        # 强制隐藏窗口
        win32gui.PostMessage(hwnd, win32con.WM_SYSCOMMAND, win32con.SC_MINIMIZE, 0)

        # 枚举所有子窗口
        def enum_child_proc(child_hwnd, _):
            try:
                win32gui.ShowWindow(child_hwnd, win32con.SW_HIDE)
            except Exception:
                pass

        win32gui.EnumChildWindows(hwnd, enum_child_proc, None)
    except Exception as e:
        print(f"错误: {e}")

def restore_window_and_children(hwnd):
    try:
        # 先恢复主窗口
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)

        # 枚举所有子窗口
        def enum_child_proc(child_hwnd, _):
            try:
                win32gui.ShowWindow(child_hwnd, win32con.SW_SHOW)
            except Exception:
                pass

        win32gui.EnumChildWindows(hwnd, enum_child_proc, None)

        # 强制聚焦回来
        win32gui.SetForegroundWindow(hwnd)

    except Exception as e:
        print(f"恢复窗口和子窗口时出错: {e}")

def resource_path(relative_path):
    """返回资源文件的绝对路径，兼容开发环境和 PyInstaller 打包后的路径"""
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller 临时目录
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

# 使用示例：加载图标
icon_path = resource_path("images/icon.png")

def setup_tray_icon():
    icon = pystray.Icon("MinimizeToTray")
    icon.icon = Image.open(resource_path('images/icon.png'))
    icon.title = "多屏桌面切换"

    icon.menu = pystray.Menu(
        item('退出', on_exit)
    )

    threading.Thread(target=keyboard_listener, daemon=True).start()
    icon.run()

def keyboard_listener():
    keyboard.add_hotkey('ctrl+alt+d', on_hotkey)
    print("监听中，按 Ctrl+Alt+D 最小化/恢复鼠标所在屏幕的窗口...")
    keyboard.wait()  # 永久阻塞

def on_exit(icon, item):
    icon.stop()
    sys.exit()

def force_set_foreground(hwnd):
    try:
        # 获取前台窗口线程和目标窗口线程
        fg_win = win32gui.GetForegroundWindow()
        fg_thread, _ = win32process.GetWindowThreadProcessId(fg_win)
        target_thread, _ = win32process.GetWindowThreadProcessId(hwnd)

        # 如果不是同一个线程，AttachThreadInput 绑定输入
        if fg_thread != target_thread:
            ctypes.windll.user32.AttachThreadInput(fg_thread, target_thread, True)
            win32gui.SetForegroundWindow(hwnd)
            ctypes.windll.user32.AttachThreadInput(fg_thread, target_thread, False)
        else:
            # 尝试调用 AllowSetForegroundWindow 让目标窗口可以设置为前台
            ctypes.windll.user32.AllowSetForegroundWindow(-1)
            win32gui.SetForegroundWindow(hwnd)
    except Exception as e:
        print(f"无法设置前台窗口: {e}")

# 开机自启
def add_to_startup():
    exe_path = sys.executable  # 获取当前运行的 exe 路径
    key = r"Software\Microsoft\Windows\CurrentVersion\Run"
    name = "Multi-DisplayDesktopSwitching"  # 启动项名称

    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key, 0, winreg.KEY_SET_VALUE) as reg_key:
            winreg.SetValueEx(reg_key, name, 0, winreg.REG_SZ, exe_path)
            print("已添加开机自启")
    except Exception as e:
        print(f"添加自启失败：{e}")

if __name__ == "__main__":
    # 不需要开机自启请关闭
    add_to_startup()

    setup_tray_icon()
