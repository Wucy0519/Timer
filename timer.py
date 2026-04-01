import tkinter as tk
from tkinter import simpledialog, messagebox
from PIL import Image
import os
import sys
import objc
from Foundation import NSObject
import AppKit


class TrayDelegate(NSObject):
    """Objective-C delegate，处理托盘菜单点击事件"""

    def initWithApp_(self, app):
        self = objc.super(TrayDelegate, self).init()
        if self is None:
            return None
        self._app = app
        return self

    def showWindow_(self, sender):
        self._app.root.after(0, self._app.root.deiconify)

    def quitApp_(self, sender):
        self._app.root.after(0, self._app.quit_app)


class CountdownApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("倒计时桌面挂件")

        # 调整窗口尺寸 宽x高
        self.root.geometry("279x45")

        # 设置窗口半透明度 (0.0 到 1.0)
        self.root.attributes('-alpha', 0.85)

        # 去掉系统标题栏，实现真正的桌面挂件，且不在任务栏显示
        self.root.overrideredirect(True)

        # 默认置顶
        self.root.attributes('-topmost', True)

        # 默认倒计时时间：2小时 (秒)
        self.default_time = 2 * 3600
        self.remaining_time = self.default_time
        self.is_running = False

        self.setup_ui()
        self.setup_drag()
        self.setup_tray()

        self.root.protocol("WM_DELETE_WINDOW", self.quit_app)
        self.root.mainloop()

    def resource_path(self, relative_path):
        """
        获取资源的绝对路径，兼容 Python 源码运行和 PyInstaller 打包后的运行环境。
        """
        try:
            # PyInstaller 创建临时文件夹，将路径存储于 _MEIPASS
            base_path = sys._MEIPASS
        except Exception:
            # 正常执行时的当前路径
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)

    def setup_ui(self):
        # 外部边框框架
        self.frame = tk.Frame(self.root, bg='#f0f0f0', highlightthickness=1, highlightbackground="#cccccc")
        self.frame.pack(expand=True, fill='both')

        # 内部主容器
        inner_frame = tk.Frame(self.frame, bg='#f0f0f0')
        inner_frame.pack(expand=True, fill='both', padx=10, pady=5)

        # 时间显示标签 (鼠标变为十字准星提示可以拖拽)
        self.time_label = tk.Label(inner_frame, text=self.format_time(self.remaining_time),
                                   font=("Arial", 16, "bold"), bg='#f0f0f0', cursor="fleur")
        self.time_label.pack(side=tk.LEFT, padx=(0, 10))

        # 按钮组
        self.start_btn = tk.Button(inner_frame, text="开始", command=self.toggle_timer, width=4)
        self.start_btn.pack(side=tk.LEFT, padx=2)

        self.reset_btn = tk.Button(inner_frame, text="重置", command=self.reset_timer, width=4)
        self.reset_btn.pack(side=tk.LEFT, padx=2)

        self.set_btn = tk.Button(inner_frame, text="设置", command=self.set_time, width=4)
        self.set_btn.pack(side=tk.LEFT, padx=2)

        # 置顶复选框
        self.topmost_var = tk.BooleanVar(value=True)
        self.topmost_cb = tk.Checkbutton(inner_frame, text="", variable=self.topmost_var,
                                         command=self.toggle_topmost, bg='#f0f0f0')
        self.topmost_cb.pack(side=tk.LEFT, padx=5)

    # ================== 鼠标拖拽功能 ==================
    def setup_drag(self):
        # 绑定鼠标事件到背景和时间标签上
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

    # ================== 系统托盘功能 (AppKit) ==================
    def setup_tray(self):
        self.tray_delegate = TrayDelegate.alloc().initWithApp_(self)

        status_bar = AppKit.NSStatusBar.systemStatusBar()
        self.status_item = status_bar.statusItemWithLength_(AppKit.NSVariableStatusItemLength)

        # 尝试加载图标
        icon_path = self.resource_path("logo.ico")
        if os.path.exists(icon_path):
            # NSImage 不支持 ico，用 PIL 转为 PNG 临时文件
            try:
                img = Image.open(icon_path)
                png_path = os.path.join(os.path.dirname(icon_path), "_logo_tmp.png")
                img.save(png_path, "PNG")
                ns_image = AppKit.NSImage.alloc().initWithContentsOfFile_(png_path)
                if ns_image:
                    ns_image.setSize_(AppKit.NSMakeSize(22, 22))
                    self.status_item.button().setImage_(ns_image)
                os.remove(png_path)
            except Exception:
                self.status_item.button().setTitle_("⏱")
        else:
            self.status_item.button().setTitle_("⏱")

        # 构建菜单
        menu = AppKit.NSMenu.alloc().init()

        show_item = AppKit.NSMenuItem.alloc().initWithTitle_action_keyEquivalent_("显示面板", "showWindow:", "")
        show_item.setTarget_(self.tray_delegate)
        menu.addItem_(show_item)

        menu.addItem_(AppKit.NSMenuItem.separatorItem())

        quit_item = AppKit.NSMenuItem.alloc().initWithTitle_action_keyEquivalent_("退出程序", "quitApp:", "")
        quit_item.setTarget_(self.tray_delegate)
        menu.addItem_(quit_item)

        self.status_item.setMenu_(menu)

    def hide_window(self):
        """隐藏主窗口"""
        self.root.withdraw()

    def quit_app(self):
        """完全退出程序"""
        # 清理托盘图标
        if hasattr(self, 'status_item'):
            AppKit.NSStatusBar.systemStatusBar().removeStatusItem_(self.status_item)
        self.root.destroy()

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
            self.root.deiconify()  # 时间到时强制弹出显示
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
            mins = simpledialog.askinteger("设置时长", "请输入倒计时时长(分钟):",
                                           parent=self.root, initialvalue=current_mins, minvalue=1)
            if mins is not None:
                self.default_time = mins * 60
                self.reset_timer()
        else:
            messagebox.showwarning("提示", "请先暂停倒计时再进行设置。")

    def toggle_topmost(self):
        self.root.attributes('-topmost', self.topmost_var.get())


if __name__ == "__main__":
    CountdownApp()
