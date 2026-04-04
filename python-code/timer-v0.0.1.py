import tkinter as tk
from tkinter import simpledialog, messagebox
import threading
import pystray
from PIL import Image, ImageDraw
import os
import sys

class CountdownApp:
    def __init__(self, root):
        self.root = root
        self.root.title("倒计时桌面挂件")
        
        # 调整窗口尺寸 宽x高
        self.root.geometry("210x28")
        
        # 设置窗口半透明度 (0.0 到 1.0)
        self.root.attributes('-alpha', 0.80)

        # 去掉系统标题栏
        self.root.overrideredirect(True)
        
        # 状态变量
        self.is_topmost = True
        self.is_visible = True
        
        # 默认置顶
        self.root.attributes('-topmost', self.is_topmost)

        # 默认倒计时时间：2小时 (秒)
        self.default_time = 2 * 3600
        self.remaining_time = self.default_time
        self.is_running = False

        self.setup_ui()
        self.setup_drag()
        self.setup_tray()

    def resource_path(self, relative_path):
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)

    def setup_ui(self):
        self.frame = tk.Frame(self.root, bg='#f0f0f0', highlightthickness=1, highlightbackground="#cccccc")
        self.frame.pack(expand=True, fill='both')

        inner_frame = tk.Frame(self.frame, bg='#f0f0f0')
        inner_frame.pack(expand=True, fill='both', padx=10, pady=5)

        self.time_label = tk.Label(inner_frame, text=self.format_time(self.remaining_time), 
                                   font=("Arial", 16, "bold"), bg='#f0f0f0', cursor="fleur")
        self.time_label.pack(side=tk.LEFT, padx=(0, 10))

        self.start_btn = tk.Button(inner_frame, text="开始", command=self.toggle_timer, width=4)
        self.start_btn.pack(side=tk.LEFT, padx=2)

        self.reset_btn = tk.Button(inner_frame, text="重置", command=self.reset_timer, width=4)
        self.reset_btn.pack(side=tk.LEFT, padx=2)

    # ================== 鼠标拖拽功能 ==================
    def setup_drag(self):
        self.frame.bind("<ButtonPress-1>", self.start_move)
        self.time_label.bind("<ButtonPress-1>", self.start_move)
        
        self.frame.bind("<B1-Motion>", self.do_move)
        self.time_label.bind("<B1-Motion>", self.do_move)

    def start_move(self, event):
        self.offset_x = event.x
        self.offset_y = event.y

    def do_move(self, event):
        x = self.root.winfo_pointerx() - self.offset_x
        y = self.root.winfo_pointery() - self.offset_y
        self.root.geometry(f"+{x}+{y}")

    # ================== 系统托盘功能 ==================
    def create_tray_icon(self):
        icon_file_name = "logo.ico"  
        icon_path = self.resource_path(icon_file_name)
        try:
            image = Image.open(icon_path)
            return image
        except Exception:
            image = Image.new('RGB', (64, 64), color='red')
            draw = ImageDraw.Draw(image)
            draw.rectangle((16, 16, 48, 48), fill=(200, 0, 0))
            return image

    def setup_tray(self):
        menu = pystray.Menu(
            pystray.MenuItem("显示面板", self.on_tray_toggle_visibility, checked=lambda item: self.is_visible, default=True),
            pystray.MenuItem("窗口置顶", self.on_tray_toggle_topmost, checked=lambda item: self.is_topmost),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("设置时间", self.on_tray_set_time),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("退出程序", self.quit_app)
        )
        self.tray_icon = pystray.Icon("timer_icon", self.create_tray_icon(), "桌面倒计时", menu)
        threading.Thread(target=self.tray_icon.run, daemon=True).start()

    # --- 托盘事件控制核心（修复状态不同步） ---
    def on_tray_toggle_visibility(self, icon, item):
        # 1. 立即改变状态
        self.is_visible = not self.is_visible
        # 2. 强制刷新托盘菜单的 UI 表现
        icon.update_menu()
        # 3. 再将窗口操作推给主线程
        if self.is_visible:
            self.root.after(0, self.root.deiconify)
        else:
            self.root.after(0, self.root.withdraw)

    def on_tray_toggle_topmost(self, icon, item):
        self.is_topmost = not self.is_topmost
        icon.update_menu()
        self.root.after(0, lambda: self.root.attributes('-topmost', self.is_topmost))

    def on_tray_set_time(self, icon, item):
        self.root.after(0, self.set_time)

    def force_show_panel(self):
        """辅助方法：当倒计时结束或设置时，如果面板隐藏则强制呼出，并同步菜单打钩状态"""
        if not self.is_visible:
            self.is_visible = True
            self.root.deiconify()
            if hasattr(self, 'tray_icon'):
                self.tray_icon.update_menu()

    def quit_app(self, icon, item):
        self.tray_icon.stop()
        self.root.after(0, self.root.destroy)

    # ================== 倒计时核心逻辑 ==================
    def format_time(self, seconds):
        h, rem = divmod(seconds, 3600)
        m, s = divmod(rem, 60)
        return f"{int(h):02d}:{int(m):02d}:{int(s):02d}"

    def update_timer(self):
        if self.is_running and self.remaining_time > 0:
            self.remaining_time -= 1
            self.time_label.config(text=self.format_time(self.remaining_time))
            self.root.after(1000, self.update_timer)
        elif self.remaining_time <= 0 and self.is_running:
            self.is_running = False
            self.start_btn.config(text="开始")
            
            # 时间到时，强制显示并置顶面板，同步菜单打钩状态
            self.force_show_panel()
            self.root.attributes('-topmost', True)
            messagebox.showinfo("时间到", "设定的倒计时已结束！")
            
            # 提示框关闭后，恢复用户原来设置的置顶状态
            self.root.attributes('-topmost', self.is_topmost)

    def toggle_timer(self):
        if self.is_running:
            self.is_running = False
            self.start_btn.config(text="继续")
        else:
            if self.remaining_time > 0:
                self.is_running = True
                self.start_btn.config(text="暂停")
                self.update_timer()

    def reset_timer(self):
        self.is_running = False
        self.remaining_time = self.default_time
        self.time_label.config(text=self.format_time(self.remaining_time))
        self.start_btn.config(text="开始")

    def set_time(self):
        self.force_show_panel() # 设置时确保面板出现并同步托盘状态
            
        if not self.is_running:
            current_mins = self.default_time // 60
            mins = simpledialog.askinteger("设置时长", "请输入倒计时时长(分钟):", parent=self.root, initialvalue=current_mins, minvalue=1)
            if mins is not None:
                self.default_time = mins * 60
                self.reset_timer()
        else:
            messagebox.showwarning("提示", "请先暂停倒计时再进行设置。")


if __name__ == "__main__":
    root = tk.Tk()
    app = CountdownApp(root)
    root.mainloop()
