import os
import sys
import subprocess
import configparser
import threading
import time
import queue
from tkinter import Tk, Toplevel, Label, Button, StringVar, messagebox
from tkinter.ttk import Combobox
from PIL import Image, ImageDraw, ImageFont
import serial.tools.list_ports
from pystray import Icon as pystray_Icon, Menu as pystray_Menu, MenuItem as pystray_MenuItem
import winshell

# --- 全域常數與設定 ---
APP_NAME = "COM Port Launcher"
SHORTCUT_NAME = f"{APP_NAME}.lnk"
CONFIG_FILE = 'com_port_config.ini'
DEFAULT_BAUD_RATE = '115200'
COMMON_BAUD_RATES = ['9600', '19200', '38400', '57600', '115200', '230400', '460800', '921600']
PUTTY_PATH = 'putty.exe' 
running_flag = True

# --- 全域變數 ---
root_tk = None
tray_icon = None
command_queue = queue.Queue()
IS_BUSY = False

# --- 設定檔處理 ---
def read_config():
    config = configparser.ConfigParser()
    if not os.path.exists(CONFIG_FILE):
        config['Settings'] = {'BaudRate': DEFAULT_BAUD_RATE}
        with open(CONFIG_FILE, 'w') as configfile:
            config.write(configfile)
    config.read(CONFIG_FILE)
    return config

def get_baud_rate():
    config = read_config()
    return config.get('Settings', 'BaudRate', fallback=DEFAULT_BAUD_RATE)

def write_baud_rate(baud_rate):
    config = read_config()
    if 'Settings' not in config:
        config.add_section('Settings')
    config.set('Settings', 'BaudRate', str(baud_rate))
    with open(CONFIG_FILE, 'w') as configfile:
        config.write(configfile)

# --- 開機自動啟動相關函式 ---
def get_shortcut_path():
    """取得捷徑應該存放的完整路徑"""
    startup_folder = winshell.startup()
    return os.path.join(startup_folder, SHORTCUT_NAME)

def is_auto_start_enabled(item):
    """
    【即時更新修正 1】
    這個函式會在每次產生選單時被 pystray 呼叫，
    直接、即時地檢查檔案是否存在。
    """
    return os.path.exists(get_shortcut_path())

def toggle_auto_start():
    """切換狀態，並在執行期間鎖定其他操作"""
    global IS_BUSY
    if IS_BUSY: return
    
    IS_BUSY = True
    shortcut_path = get_shortcut_path()
    message = ""
    
    # 【即時更新修正 2】直接讀取當前的檔案狀態來決定要執行的操作
    if os.path.exists(shortcut_path):
        try:
            os.remove(shortcut_path)
            message = "已取消開機自動啟動。"
        except Exception as e:
            message = f"取消開機啟動時發生錯誤: {e}"
    else:
        try:
            target_path = sys.executable
            with winshell.shortcut(shortcut_path) as shortcut:
                shortcut.path = target_path
                shortcut.description = f"{APP_NAME} - COM Port 工具"
                shortcut.working_directory = os.path.dirname(target_path)
            message = "已設定開機自動啟動。"
        except Exception as e:
            message = f"設定開機啟動時發生錯誤: {e}"
    
    print(message)
    if tray_icon:
        tray_icon.notify(message, title=APP_NAME)
    
    IS_BUSY = False

# --- PuTTY 相關 ---
def launch_putty(port_device):
    baud_rate = get_baud_rate()
    print(f"準備開啟 PuTTY -> Port: {port_device}, Baud: {baud_rate}")
    try:
        command = [PUTTY_PATH, '-serial', port_device, '-sercfg', f'{baud_rate},8,n,1,N']
        subprocess.Popen(command)
    except FileNotFoundError:
        error_msg = f"錯誤: 找不到 '{PUTTY_PATH}'。"
        print(error_msg)
        messagebox.showerror("PuTTY 執行錯誤", error_msg)
    except Exception as e:
        print(f"啟動 PuTTY 時發生錯誤: {e}")

# --- 工廠函式 (執行緒安全) ---
def create_putty_launcher(port_name_str):
    def launcher():
        command_queue.put(f"LAUNCH_PUTTY:{port_name_str}")
    return launcher

# --- GUI 視窗 ---
def open_baud_rate_window():
    global IS_BUSY
    if IS_BUSY: return
    IS_BUSY = True

    def close_and_release_lock():
        global IS_BUSY
        IS_BUSY = False
        window.destroy()

    def on_save():
        new_baud = combo_var.get()
        if new_baud and new_baud.isdigit():
            write_baud_rate(new_baud)
            print(f"鮑率已儲存為: {new_baud}")
            close_and_release_lock()
        else:
            messagebox.showerror("錯誤", "請輸入有效的數字鮑率。", parent=window)
            
    try:
        window = Toplevel(root_tk)
        window.title("設定預設鮑率")
        window.attributes("-topmost", True)
        window.protocol("WM_DELETE_WINDOW", close_and_release_lock)
        
        Label(window, text="請選擇或輸入鮑率:").pack(pady=10)
        combo_var = StringVar()
        combobox = Combobox(window, textvariable=combo_var)
        combobox['values'] = COMMON_BAUD_RATES
        combobox.set(get_baud_rate())
        combobox.pack(padx=20, fill='x')
        btn_frame = Label(window)
        Button(btn_frame, text="儲存", command=on_save).pack(side='left', padx=10, pady=10)
        Button(btn_frame, text="取消", command=close_and_release_lock).pack(side='left', padx=10, pady=10)
        btn_frame.pack()
        window.update_idletasks()
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        window_width = 300
        window_height = 120
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)
        window.geometry(f'{window_width}x{window_height}+{x}+{y}')
        window.focus_force()
    except Exception as e:
        print(f"### 錯誤 ### 在建立 Tkinter 視窗時發生問題: {e}")
        IS_BUSY = False

# --- 系統匣圖示 ---
def create_icon_image():
    width, height = 64, 64
    image = Image.new('RGB', (width, height), color=(30, 144, 255))
    draw = ImageDraw.Draw(image)
    try:
        font = ImageFont.truetype("consola.ttf", 38)
    except IOError:
        font = ImageFont.load_default()
    if hasattr(draw, 'textbbox'):
        _, _, w, h = draw.textbbox((0, 0), "COM", font=font)
    else:
        w, h = draw.textsize("COM", font=font)
    draw.text(((width - w) / 2, (height - h) / 2 - 5), "COM", fill=(255, 255, 255), font=font)
    return image

def update_tooltip(icon):
    while running_flag:
        try:
            baud_rate_info = f"預設鮑率: {get_baud_rate()}\n"
            ports = serial.tools.list_ports.comports()
            if not ports:
                tooltip_text = baud_rate_info + "目前找不到任何 COM Port"
            else:
                port_list = [f"{p.device}: {p.description}" for p in ports]
                tooltip_text = baud_rate_info + "--------------------\n" + "\n".join(port_list)
            icon.title = tooltip_text
            time.sleep(3)
        except Exception as e:
            if running_flag: print(f"更新 Tooltip 時發生錯誤: {e}")
            time.sleep(10)

def exit_application():
    global running_flag
    print("正在關閉應用程式...")
    running_flag = False
    if tray_icon:
        tray_icon.stop()
    if root_tk:
        root_tk.destroy()

def generate_dynamic_menu():
    """產生動態選單，並根據 IS_BUSY 旗標決定項目是否可用"""
    ports = serial.tools.list_ports.comports()
    if ports:
        for port in ports:
            yield pystray_MenuItem(
                f"開啟 {port.device}", 
                action=create_putty_launcher(port.device),
                enabled=not IS_BUSY
            )
        yield pystray_Menu.SEPARATOR
    
    # 【即時更新修正 3】checked 參數現在直接呼叫即時檢查函式
    yield pystray_MenuItem(
        "開機時自動啟動",
        lambda: command_queue.put("TOGGLE_AUTO_START"),
        checked=is_auto_start_enabled,
        enabled=not IS_BUSY
    )
    
    yield pystray_MenuItem(
        '設定鮑率...', 
        lambda: command_queue.put("OPEN_BAUD_WINDOW"),
        enabled=not IS_BUSY
    )
    
    yield pystray_MenuItem('離開', lambda: command_queue.put("EXIT"), enabled=True)

# --- 主程式 ---
def process_queue():
    try:
        command = command_queue.get_nowait()
        if command.startswith("LAUNCH_PUTTY:"):
            port = command.split(":", 1)[1]
            launch_putty(port)
        elif command == "TOGGLE_AUTO_START":
            toggle_auto_start()
        elif command == "OPEN_BAUD_WINDOW":
            open_baud_rate_window()
        elif command == "EXIT":
            exit_application()
    except queue.Empty:
        pass
    finally:
        if running_flag:
            root_tk.after(100, process_queue)

def main():
    global root_tk, tray_icon
    root_tk = Tk()
    root_tk.withdraw()
    
    # 【即時更新修正 4】不再需要在啟動時檢查初始狀態
    # check_initial_auto_start_state() # 這行已不再需要

    image = create_icon_image()
    menu = pystray_Menu(generate_dynamic_menu)
    tray_icon = pystray_Icon(APP_NAME, image, "正在啟動...", menu)
    tray_thread = threading.Thread(target=tray_icon.run, daemon=True)
    tray_thread.start()
    tooltip_thread = threading.Thread(target=update_tooltip, args=(tray_icon,), daemon=True)
    tooltip_thread.start()
    print(f"應用程式 '{APP_NAME}' 已啟動。")
    root_tk.after(100, process_queue)
    root_tk.mainloop()
    print(f"應用程式 '{APP_NAME}' 已關閉。")

if __name__ == "__main__":
    main()