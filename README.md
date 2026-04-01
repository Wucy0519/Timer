# ⏳ Desktop Countdown Timer 

[English](README.md) **|** [简体中文](README_CN.md) 

This is a lightweight desktop countdown widget developed using Python. It features a semi-transparent, borderless, and freely draggable design. Once running, it automatically hides its taskbar icon and quietly resides in the system tray in the bottom right corner, ensuring it doesn't disrupt your daily workflow.

## ✨ Core Features

* **Minimalist Visuals:** Semi-transparent and borderless design that takes up minimal screen space.
* **Freely Draggable:** Click and hold any blank area or the time digits to freely move the widget anywhere on your desktop.
* **Flexible Settings:** Defaults to a 2-hour countdown, but you can customize the duration (in minutes) at any time via the "Settings" button.
* **One-Click Pin to Top:** Provides a pin-to-top option (the text label for this is hidden for a cleaner look), ensuring the countdown is always visible above other windows.

---

## 📸 Usage Tutorial

### 1. Run the Program
You can directly download the packaged `.exe` file and double-click to run it. No Python environment configuration is required.

### 2. Main Interface and Pin to Top
The interface is compact and intuitive, containing "Start/Pause", "Reset", and "Settings" buttons. Check the rightmost checkbox to keep the widget pinned to the top of all other windows.

### 3. System Tray Background Operation
To keep your taskbar clean, this program does not display an icon on the bottom taskbar. You can find it in the Windows system tray in the bottom right corner of your screen. Right-click the tray icon to select "Show Panel" or "Exit Program".

---

## 📁 Directory Structure

```text
.
├── asset/                 # Contains screenshots and icon resources used in the README
│   ├── 0.png
│   ├── 1.png
│   └── 2.png
├── python-code/           # Contains Python source code
│   ├── timer.py           # Main program code
│   └── my_icon.ico        # System tray icon source file
└── README.md              # Project documentation