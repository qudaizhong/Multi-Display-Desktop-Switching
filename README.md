# Multi-Display Desktop Switching 多屏桌面切换

## 简介
这是一个用 Python 开发的 Windows 下多屏快速切换桌面的工具。它允许用户通过快捷键切换当前屏幕到桌面，而不影响其他屏幕上的窗口，专为多显示器用户设计，提升多屏工作环境的效率。

## 为什么写它
在使用多屏显示的过程中，我常常遇到需要将 **屏幕 1** 切换到桌面，但不希望影响 **其他屏幕的窗口**。虽然 `Win + D` 可以快速回到桌面，但它会影响所有屏幕上的窗口，而我仅仅需要切换一个屏幕。

网上找不到合适的工具来实现这个功能，因此我决定自己动手编写这个小工具来解决这一问题。经过一些尝试和调整，最终开发出了这个桌面切换工具，且完全免费开源。

## 功能
- **快捷键支持**：支持快捷键 `Ctrl + Alt + D`，切换当前鼠标所在屏幕到桌面，其他屏幕保持不变。
- **多屏支持**：可以支持多屏工作环境，操作时不会影响其他屏幕的显示。
- **开机自启**：程序支持自动加开机自启，启动后无需手动打开。
- **轻量化设计**：使用 `PyInstaller` 打包为单一 `.exe` 文件，便于分发与使用。

## 安装与使用方法

### 1. 安装依赖
在开始之前，确保你已经安装了所有依赖库。如果你使用虚拟环境，可以通过以下命令安装依赖：

```bash
pip install -r requirements.txt
```

`requirements.txt` 文件包含了所有需要的第三方库。

### 2. 打包

#### 2.1 虚拟环境打包
如果你使用的是 **`venv`** 虚拟环境，建议在 `.venv\Scripts\` 目录下执行以下打包命令：

```bash
pyinstaller --name "Multi-DisplayDesktopSwitching" --onefile --add-data "..\..\images\icon.png;images" --windowed --icon=..\..\images\icon.png ..\..\main.py --distpath ..\..\dist
```

#### 2.2 真实环境下打包
在项目根目录下执行以下打包命令：

```bash
pyinstaller --name "Multi-DisplayDesktopSwitching" --onefile --add-data ".\images\icon.png;images" --windowed --icon=.\images\icon.png .\main.py
```

### 3. 打包后的 `exe` 文件
生成的 `.exe` 文件会保存在 `dist` 文件夹中。运行该文件后，程序会自动添加到开机自启。若不需要开机自启，请在 `main.py` 文件中注释掉 `add_to_startup()` 函数的调用。

### 4. 配置与图标
- 程序默认会加载 `images/icon.png` 作为图标，并且支持在界面中展示该图标。
- 如果你想自定义图标，可以替换 `images/icon.png` 文件，或在打包命令中指定自己的图标。

## 使用说明

### 快捷键
- **Ctrl + Alt + D**：显示/隐藏鼠标当前所在屏幕的窗口。

### 其他设置
- 若你不想让程序开机自启，可以在 `main.py` 中注释掉以下行代码：

  ```python
  add_to_startup()
  ```

## 项目目录结构

```
Multi-Display-Desktop-Switching/
├── .venv/                  ← 虚拟环境目录
├── images/                 ← 图标等资源
├── main.py                 ← 主程序入口
├── README.md               ← 项目说明
├── requirements.txt        ← 依赖清单
├── .gitignore              ← 忽略文件列表
└── LICENSE                 ← 开源许可证
```

## 问题排查

- **exe 无法运行**：确保你已安装所有依赖并正确执行了打包命令。如果程序没有任何反应，尝试在命令行中运行 `.exe`，查看是否有错误输出。
- **快捷键无法工作**：检查系统是否已经绑定了其他的 `Ctrl + Alt + D` 快捷键，或者是否存在与系统设置的冲突。

## 许可证

该项目使用 [MIT License](./LICENSE) 开源。
```
