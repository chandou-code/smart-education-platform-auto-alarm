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

## 快速开始

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

### 3. 启动服务

```bash
# 一键启动（推荐）
python 启动.py

# 或者分别启动
python start_server.py # 启动服务器
python gui/tray.py  # 启动主程序（GUI版）
```

### 4. 手机订阅日历

1. 打开手机日历应用
2. 选择「从URL导入」或「订阅日历」
3. 输入局域网地址，如：
   ```
   http://192.168.1.100:8000/calendar.ics
   ```

### 5. 使用

1. 打开国家高等教育智慧教育平台，进入网课播放页面
2. 按 **F9** 键生成闹钟
3. 手机日历会自动同步，视频结束前响铃提醒
4. 按 **ESC** 键退出程序

### 6. 配置

如需修改截图区域：
```bash
python gui/config_window.py
```

## 实际使用体验

导入URL后，服务器一更新ICS，小米日历就会自动同步！手机啥操作都不用管，平时刷刷抖音就行，到点闹钟一响，点开网课页面按个F9日历就帮你定好闹钟了。

### 工作流

1. 📺 **网课播放** - 国家高等教育智慧教育平台播放视频
2. ⌨️ **F9 更新** - 按一下 F9，程序自动：
   - 唤醒 Edge 浏览器
   - 调整到屏幕右半边
   - 截图识别视频时长
   - 生成 ICS 日历闹钟
3. 📱 **自动同步** - 手机不需要任何操作，小米日历会定期（15-30分钟）检查订阅的 URL 并自动更新
4. 📢 **闹钟提醒** - 视频结束前自动响铃
5. 🔄 **循环往复** - 继续下一课，重复上面步骤

## 技术实现

### 模块架构

项目采用模块化设计：

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

### 工作原理

#### OCR 识别流程
1. **截图**：截取视频时长显示区域
2. **预处理**：放大、灰度化、对比度增强、二值化
3. **识别**：使用Tesseract进行文字识别
4. **解析**：提取时间格式并计算分钟数

#### 日历同步原理
这得益于 **ICS 订阅机制**：
- 小米日历会定期（15-30分钟）检查订阅的 URL
- 当服务器更新 `course_alarm.ics` 文件时
- 手机日历检测到变化就会自动拉取最新版本
- 同一个 UID 的事件会被更新，而不会重复创建

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
