# 国家高等教育智慧教育平台 - 网课自动提醒系统

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)

## 项目简介

本项目为国家高等教育智慧教育平台提供网课自动提醒功能。当你在电脑上刷网课时，可以使用手机通过局域网URL导入日历，自动接收网课结束提醒，让你可以安心玩手机。

## 核心功能

- **自动截图识别**：自动截取视频时长并进行OCR识别
- **智能闹钟生成**：根据视频时长自动生成ICS日历闹钟
- **局域网同步**：手机通过URL订阅日历，实时同步更新
- **热键触发**：按 F9 键快速更新闹钟
- **可视化配置**：GUI配置工具，支持可视化选择截图区域
- **系统托盘**：支持系统托盘图标，后台运行不打扰
- **实时状态监控**：显示识别结果和下次提醒时间
- **自动唤醒浏览器**：自动唤醒Edge浏览器并调整到屏幕右侧

## 安装步骤

### 1. 安装依赖

```bash
pip install pyautogui pillow pytesseract keyboard
```

（可选）安装系统托盘图标依赖：
```bash
pip install pystray
```

### 2. 安装 Tesseract OCR

下载并安装 Tesseract：
- Windows: https://github.com/UB-Mannheim/tesseract/wiki
- 安装时选择中文语言包

### 3. 启动服务（推荐）

```bash
# 一键启动（推荐）
python 启动.py

# 或者分别启动
python start_server.py # 启动服务器
python main.py  # 启动主程序（命令行版）
python gui/tray.py  # 启动主程序（GUI版）
```

## 使用方法

### 第一步：准备工作

1. 打开国家高等教育智慧教育平台
2. 进入网课播放页面

### 第二步：启动服务

```bash
# 一键启动（推荐）
python 启动.py
```

### 第三步：手机订阅日历

1. 打开手机日历应用
2. 选择「从URL导入」或「订阅日历」
3. 输入局域网地址，如：
   ```
   http://192.168.1.100:8000/calendar.ics
   ```

### 第四步：开始刷课

1. 开始播放网课
2. 按 **F9** 键生成闹钟
3. 系统会自动：
   - 唤醒Edge浏览器并调整到屏幕右侧
   - 点击浏览器激活窗口
   - 触发视频进度条显示
   - 截图识别视频时长
   - 生成日历闹钟

### 第五步：配置工具

如需修改截图区域：

```bash
# 打开配置窗口
python gui/config_window.py
```

### 退出程序

按 **ESC** 键退出

## 功能说明

### 模块架构

项目采用模块化设计，功能独立：

| 模块 | 功能 |
|------|------|
| core/config.py | 配置管理（JSON持久化） |
| core/screenshotter.py | 截图与鼠标操作 |
| core/ocr_engine.py | OCR识别与时间解析 |
| core/ics_generator.py | ICS日历生成 |
| core/window_manager.py | Edge浏览器窗口管理 |
| server/http_server.py | HTTP文件服务 |
| client/hotkey_listener.py | 热键监听 |
| gui/tray.py | GUI主程序与状态监控 |
| gui/config_window.py | 可视化配置界面 |

### GUI主程序功能

- 显示实时状态
- 上次识别结果
- 下次提醒倒计时
- 操作日志记录
- 一键生成闹钟按钮
- 配置按钮
- 系统托盘图标（可选）

### 浏览器控制

- 自动唤醒Edge浏览器
- 自动调整到屏幕右半屏
- 恢复、置顶、设置焦点
- 最大化视频播放区域

## 技术原理

### OCR识别流程

1. **截图**：截取视频时长显示区域
2. **预处理**：放大、灰度化、对比度增强、二值化
3. **识别**：使用Tesseract进行文字识别
4. **解析**：提取时间格式并计算分钟数

### 日历同步原理

1. 生成标准ICS格式日历文件
2. 通过HTTP服务器提供文件访问
3. 手机订阅URL自动同步更新
4. 同一UID，更新时不重复创建事件

## 文件结构

```
.
├── 启动.py          # 一键启动脚本
├── main.py          # 命令行版主程序
├── start_server.py  # ICS服务器启动脚本
├── decode_tool.py   # Base64解码工具
├── config.json      # 配置文件（自动生成）
├── course_alarm.ics # 生成的日历文件（自动生成）
├── core/              # 核心模块
│   ├── __init__.py
│   ├── config.py       # 配置管理
│   ├── screenshotter.py  # 截图模块
│   ├── ocr_engine.py   # OCR识别模块
│   ├── ics_generator.py # ICS生成模块
│   └── window_manager.py # 窗口管理模块
├── server/            # 服务端模块
│   ├── __init__.py
│   └── http_server.py   # HTTP服务器
├── client/           # 客户端模块
│   ├── __init__.py
│   └── hotkey_listener.py  # 热键监听
├── gui/              # GUI模块
│   ├── __init__.py
│   ├── config_window.py  # 配置窗口
│   └── tray.py          # 系统托盘与状态监控
└── README.md          # 项目说明文档
```

## 配置说明

默认配置参数（config.json）：

```json
{
  "screenshot": {
    "start_x": 2357, "start_y": 1104,
    "end_x": 2286, "end_y": 1047,
    "click_x": 2054, "click_y": 30
  },
  "ocr": {
    "lang": "chi_sim+eng",
    "psm": 7,
    "contrast": 2.0,
    "threshold": 128,
    "scale_factor": 2
  },
  "ics": {
    "uid": "course_alarm@coursereminder",
    "alarm_duration_minutes": 5,
    "timezone": "Asia/Shanghai",
    "calendar_name": "刷课闹钟"
  },
  "server": {
    "port": 8000,
    "host": ""
  },
  "hotkey": {
    "trigger_key": "f9",
    "exit_key": "esc"
  }
}
```

## 注意事项

1. 确保电脑和手机在同一局域网内
2. 首次使用需在手机日历中订阅URL
3. 如果识别失败，检查视频时长是否清晰显示
4. 使用Edge浏览器以实现自动唤醒
5. 首次运行请先使用配置工具选择正确的截图区域

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request！