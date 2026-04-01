import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import os
import sys
import objc
from Foundation import NSObject
import AppKit

# 颜色主题
BG = '#2d2d2d'
BG_BTN = '#3c3c3c'
BG_HOVER = '#505050'
FG = '#d4d4d4'
FG_DIM = '#777777'
ACCENT = '#5ba0f5'


class TrayDelegate(NSObject):

    def initWithApp_(self, app):
        self = objc.super(TrayDelegate, self).init()
        if self is None:
            return None
        self._app = app
        return self

    def showWindow_(self, sender):
        try:
            self._app.root.after(0, lambda: self._app.root.deiconify())
        except Exception:
            pass

    def quitApp_(self, sender):
        try:
            self._app.root.after(0, self._app.quit_app)
        except Exception:
            pass


class CountdownApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("倒计时")
        AppKit.NSApplication.sharedApplication().setActivationPolicy_(
            AppKit.NSApplicationActivationPolicyRegular)
        self.root.configure(bg=BG)
        self.root.geometry("360x50")
        self.root.resizable(False, False)

        self.default_time = 2 * 3600
        self.remaining_time = self.default_time
        self.is_running = False
        self.topmost = False
        self._quitting = False

        self._set_icon()
        self.setup_ui()
        self.setup_tray()

        self.root.protocol("WM_DELETE_WINDOW", self.quit_app)
        self.root.mainloop()

    def _set_icon(self):
        icon_path = self.resource_path("logo.ico")
        if os.path.exists(icon_path):
            try:
                img = Image.open(icon_path)
                img = img.resize((64, 64), Image.LANCZOS)
                self._icon_img = ImageTk.PhotoImage(img)
                self.root.iconphoto(True, self._icon_img)
            except Exception:
                pass

    def resource_path(self, relative_path):
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)

    # ================== UI ==================
    def setup_ui(self):
        inner = tk.Frame(self.root, bg=BG, bd=0, highlightthickness=0)
        inner.pack(expand=True, fill='both', padx=12, pady=8)

        # ---- 时 : 分 : 秒 (三个 Entry，始终可聚焦) ----
        efont = ("Menlo", 22, "bold")
        common = dict(font=efont, fg=ACCENT, bg=BG, insertbackground=ACCENT,
                      width=2, justify='center', relief='flat', bd=0,
                      highlightthickness=0, readonlybackground=BG)

        self.hour_e = tk.Entry(inner, **common)
        self.sep1 = tk.Label(inner, text=":", font=efont, fg=ACCENT, bg=BG)
        self.min_e = tk.Entry(inner, **common)
        self.sep2 = tk.Label(inner, text=":", font=efont, fg=ACCENT, bg=BG)
        self.sec_e = tk.Entry(inner, **common)

        for w in (self.hour_e, self.sep1, self.min_e, self.sep2, self.sec_e):
            w.pack(side=tk.LEFT)

        self._all_entries = [self.hour_e, self.min_e, self.sec_e]
        self._fill_entries()

        for e in self._all_entries:
            e.bind('<FocusIn>', self._on_focus_in)
            e.bind('<Return>', self._on_confirm)
            e.bind('<Escape>', lambda ev: self.root.focus_set())
            e.bind('<KeyRelease>', self._on_key)

        # ---- 分隔线 ----
        tk.Frame(inner, bg='#444', width=1).pack(side=tk.LEFT, fill='y', padx=8, pady=4)

        # ---- 按钮 ----
        self.start_btn = self._make_btn(inner, "开始", self.toggle_timer,
                                        bg=ACCENT, fg='white')
        self.start_btn.pack(side=tk.LEFT, padx=2)

        self._make_btn(inner, "重置", self.reset_timer).pack(side=tk.LEFT, padx=2)

        self.pin_btn = self._make_btn(inner, "📌", self.toggle_topmost)
        self.pin_btn.pack(side=tk.LEFT, padx=2)

    def _make_btn(self, parent, text, cmd, bg=BG_BTN, fg=FG):
        b = tk.Label(parent, text=text, font=("PingFang SC", 11),
                     bg=bg, fg=fg, cursor='hand2', padx=8, pady=2)
        b.bind('<Button-1>', lambda e: cmd())
        b.bind('<Enter>', lambda e: b.config(bg=BG_HOVER))
        b.bind('<Leave>', lambda e: b.config(bg=bg))
        b._bg = bg
        return b

    # ---- 时间 Entry 交互 ----
    def _fill_entries(self):
        h, rem = divmod(self.remaining_time, 3600)
        m, s = divmod(rem, 60)
        for entry, val in zip(self._all_entries, [h, m, s]):
            st = entry.cget('state')
            entry.config(state='normal')
            entry.delete(0, tk.END)
            entry.insert(0, f"{val:02d}")
            entry.config(state=st if st == 'readonly' else 'normal')

    def _on_focus_in(self, event):
        if self.is_running:
            self.root.focus_set()
            return
        event.widget.select_range(0, tk.END)

    def _on_key(self, event):
        if self.is_running:
            return
        e = event.widget
        # 输入满 2 位自动跳到下一个
        if event.keysym in ('BackSpace', 'Delete', 'Left', 'Right',
                            'Shift_L', 'Shift_R', 'Tab'):
            return
        if len(e.get()) >= 2 and event.char.isdigit():
            idx = self._all_entries.index(e)
            if idx < 2:
                self._all_entries[idx + 1].focus_set()
            else:
                self._on_confirm()

    def _on_confirm(self, event=None):
        try:
            h = int(self.hour_e.get())
            m = int(self.min_e.get())
            s = int(self.sec_e.get())
            total = h * 3600 + m * 60 + s
            if total >= 1:
                self.default_time = total
                self.remaining_time = total
        except ValueError:
            pass
        self._fill_entries()
        self.root.focus_set()

    # ================== 系统托盘 ==================
    def setup_tray(self):
        self.tray_delegate = TrayDelegate.alloc().initWithApp_(self)
        status_bar = AppKit.NSStatusBar.systemStatusBar()
        self.status_item = status_bar.statusItemWithLength_(AppKit.NSVariableStatusItemLength)

        icon_path = self.resource_path("logo.ico")
        if os.path.exists(icon_path):
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

        menu = AppKit.NSMenu.alloc().init()
        show_item = AppKit.NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
            "显示面板", "showWindow:", "")
        show_item.setTarget_(self.tray_delegate)
        menu.addItem_(show_item)
        menu.addItem_(AppKit.NSMenuItem.separatorItem())
        quit_item = AppKit.NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
            "退出程序", "quitApp:", "")
        quit_item.setTarget_(self.tray_delegate)
        menu.addItem_(quit_item)
        self.status_item.setMenu_(menu)

    def quit_app(self):
        if self._quitting:
            return
        self._quitting = True
        self.is_running = False
        if hasattr(self, 'status_item'):
            AppKit.NSStatusBar.systemStatusBar().removeStatusItem_(self.status_item)
        self.root.destroy()

    # ================== 倒计时逻辑 ==================
    def update_timer(self):
        if self._quitting:
            return
        if self.is_running and self.remaining_time > 0:
            self.remaining_time -= 1
            # 倒计时中直接更新文字，不触发状态切换
            h, rem = divmod(self.remaining_time, 3600)
            m, s = divmod(rem, 60)
            for entry, val in zip(self._all_entries, [h, m, s]):
                entry.delete(0, tk.END)
                entry.insert(0, f"{val:02d}")
            self.root.after(1000, self.update_timer)
        elif self.remaining_time <= 0 and self.is_running:
            self.is_running = False
            self.start_btn.config(text="开始")
            self._fill_entries()
            self.root.deiconify()
            messagebox.showinfo("时间到", "设定的倒计时已结束！")

    def toggle_timer(self):
        if self.is_running:
            self.is_running = False
            self.start_btn.config(text="开始")
        else:
            if self.remaining_time > 0:
                # 启动前先读取当前输入值
                self._on_confirm()
                if self.remaining_time > 0:
                    self.is_running = True
                    self.start_btn.config(text="暂停")
                    self.update_timer()

    def reset_timer(self):
        self.is_running = False
        self.remaining_time = self.default_time
        self._fill_entries()
        self.start_btn.config(text="开始")

    def toggle_topmost(self):
        self.topmost = not self.topmost
        self.root.attributes('-topmost', self.topmost)
        if self.topmost:
            self.pin_btn.config(text="📍")
        else:
            self.pin_btn.config(text="📌")


if __name__ == "__main__":
    import _tkinter
    lib_dir = os.path.dirname(os.path.dirname(os.path.dirname(_tkinter.__file__)))
    for name, subdir in [("TCL_LIBRARY", "tcl9.0"), ("TK_LIBRARY", "tk9.0")]:
        if name not in os.environ:
            path = os.path.join(lib_dir, subdir)
            if os.path.isdir(path):
                os.environ[name] = path
    CountdownApp()
