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
        
        self.root.geometry("279x45")
        
        self.root.attributes('-alpha', 0.85)
        self.root.overrideredirect(True)
        
        self.root.attributes('-topmost', True)

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

        self.set_btn = tk.Button(inner_frame, text="设置", command=self.set_time, width=4)
        self.set_btn.pack(side=tk.LEFT, padx=2)

        self.topmost_var = tk.BooleanVar(value=True)
        self.topmost_cb = tk.Checkbutton(inner_frame, text="", variable=self.topmost_var, 
                                         command=self.toggle_topmost, bg='#f0f0f0')
        self.topmost_cb.pack(side=tk.LEFT, padx=5)

    def setup_drag(self):
        self.frame.bind("<ButtonPress-1>", self.start_move)
        self.frame.bind("<ButtonRelease-1>", self.stop_move)
        self.frame.bind("<B1-Motion>", self.do_move)
        
        self.time_label.bind("<ButtonPress-1>", self.start_move)
        self.time_label.bind("<ButtonRelease-1>", self.stop_move)
        self.time_label.bind("<B1-Motion>", self.do_move)

    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def stop_move(self, event):
        self.x = None
        self.y = None

    def do_move(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.root.winfo_x() + deltax
        y = self.root.winfo_y() + deltay
        self.root.geometry(f"+{x}+{y}")

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
            pystray.MenuItem("显示面板", self.show_window_from_tray, default=True),
            pystray.MenuItem("退出程序", self.quit_app)
        )
        self.tray_icon = pystray.Icon("timer_icon", self.create_tray_icon(), "桌面倒计时", menu)
        
        threading.Thread(target=self.tray_icon.run, daemon=True).start()

    def hide_window(self):
        self.root.withdraw()

    def show_window_from_tray(self, icon, item):
        self.root.after(0, self.root.deiconify)

    def quit_app(self, icon, item):
        self.tray_icon.stop()
        self.root.after(0, self.root.destroy)

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
            self.root.deiconify() # 时间到时强制弹出显示
            messagebox.showinfo("时间到", "设定的倒计时已结束！")

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
        if not self.is_running:
            current_mins = self.default_time // 60
            mins = simpledialog.askinteger("设置时长", "请输入倒计时时长(分钟):", parent=self.root, initialvalue=current_mins, minvalue=1)
            if mins is not None:
                self.default_time = mins * 60
                self.reset_timer()
        else:
            messagebox.showwarning("提示", "请先暂停倒计时再进行设置。")

    def toggle_topmost(self):
        self.root.attributes('-topmost', self.topmost_var.get())

if __name__ == "__main__":
    root = tk.Tk()
    app = CountdownApp(root)
    root.mainloop()
