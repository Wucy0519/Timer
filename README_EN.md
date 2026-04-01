# ⏳ Desktop Countdown Timer
English | [简体中文](./README_CN.md)

This is a lightweight desktop countdown widget developed in Python. It features a translucent, borderless, and draggable interface. Once launched, it automatically hides its taskbar icon and resides silently in the system tray (bottom-right corner), ensuring it doesn't interrupt your daily workflow.

**Windows EXE Download Links:**  [Google Drive](https://drive.google.com/file/d/1K8Xy5-gPybSjm8b4Lrwx4peJPUTRuhJm/view?usp=sharing) | [百度网盘](https://pan.baidu.com/s/1KmjRVwZq6DcGX2PSPdfjJg?pwd=c3s8)

---

## ✨ Core Features

* **Minimalist Visuals:** Translucent and borderless design that occupies minimal screen real estate.
* **Free Dragging:** Simply click and hold any blank area or the timer digits to move the widget anywhere on your desktop.
* **Flexible Settings:** Default countdown is set to 2 hours; you can customize the duration (in minutes) at any time via the "Settings" button.
* **Always on Top:** Includes a "Pin" option (with a hidden "Pin" label) to ensure the countdown remains visible above all other windows.

---

## 📸 Usage Tutorial

### 1. Run the Program
You can directly download the packaged `.exe` file and double-click to run it. No Python environment configuration is required.

### 2. Main Interface & Pinning
The interface is compact and intuitive, featuring **Start/Pause**, **Reset**, and **Settings** buttons. Check the checkbox on the far right to enable the "Always on Top" mode, keeping the widget in the foreground.

### 3. System Tray (Background Running)
To keep your taskbar clean, the program does not display a standard taskbar icon. You can find it in the Windows System Tray (bottom-right corner). Right-click the tray icon to select **"Show Panel"** or **"Exit"**.

---

## 📁 Directory Structure

```text
.
├── asset/                # Screenshots and icon resources for README
│   ├── 0.png
│   ├── 1.png
│   └── 2.png
├── python-code/          # Python source code
│   ├── timer.py          # Main program logic
│   └── logo.ico          # Source file for the tray icon
└── README.md             # Project documentation
```

---

## 📦 Packaging as EXE

To package the script yourself, you need to install the following Python libraries:
```shell
pystray
Pillow
pyinstaller
```
Ensure your terminal/command prompt path is set to the same folder containing `timer.py` and `logo.ico`. Run the following command (Windows example):

```shell
pyinstaller -F -w --add-data "logo.ico;." -i logo.ico timer.py
```

Once completed, retrieve the generated `timer.exe` from the `dist` folder. The icon is perfectly encapsulated within the executable, allowing you to run the file from any location on your computer.

---

## ⚠️ Special Notice

**Commercial use is strictly prohibited.** For commercial inquiries, please contact: **chenyangwu@mail.nankai.edu.cn**
