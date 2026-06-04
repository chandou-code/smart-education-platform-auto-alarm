#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系统托盘与实时状态监控
"""

# 抑制 libpng iCCP 警告
import warnings
warnings.filterwarnings("ignore", category=UserWarning, message="iCCP")

import tkinter as tk
from tkinter import ttk
import threading
import time
from datetime import datetime, timedelta
import os
import sys
from typing import Optional

# 添加模块路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.config import ConfigManager


class TrayIcon:
    """系统托盘图标"""
    
    def __init__(self, app):
        self.app = app
        self.root = tk.Toplevel()
        self.root.withdraw()
        
        # 尝试使用 pystray，如果没有则使用简单窗口
        try:
            import pystray
            from PIL import Image
            self._init_pystray()
        except ImportError:
            self._init_simple()
    
    def _init_pystray(self):
        """使用 pystray 实现托盘图标"""
        try:
            import pystray
            from PIL import Image
            
            # 创建简单图标
            icon = Image.new('RGB', (64, 64), color='blue')
            
            menu = pystray.Menu(
                pystray.MenuItem("显示主窗口", self.show_main),
                pystray.MenuItem("生成闹钟", self.trigger_alarm),
                pystray.MenuItem("配置", self.show_config),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem("退出", self.quit)
            )
            
            self.icon = pystray.Icon("course_alarm", icon, "刷课闹钟", menu)
            
            # 在单独线程运行
            self.thread = threading.Thread(target=self._run_pystray, daemon=True)
            self.thread.start()
            
        except Exception as e:
            print(f"托盘图标初始化失败: {e}")
            self._init_simple()
    
    def _init_simple(self):
        """简单实现 - 无托盘图标"""
        self.icon = None
        self.app.show_main_window()
    
    def _run_pystray(self):
        """运行托盘图标"""
        self.icon.run()
    
    def show_main(self, icon=None, item=None):
        """显示主窗口"""
        self.app.show_main_window()
    
    def trigger_alarm(self, icon=None, item=None):
        """触发闹钟生成"""
        self.app.trigger_alarm()
    
    def show_config(self, icon=None, item=None):
        """显示配置窗口"""
        self.app.show_config_window()
    
    def quit(self, icon=None, item=None):
        """退出"""
        self.app.quit()
        if self.icon:
            self.icon.stop()
    
    def stop(self):
        """停止托盘"""
        if self.icon:
            self.icon.stop()


class StatusWindow:
    """状态窗口 - 显示实时状态"""
    
    def __init__(self, root, app):
        self.root = root
        self.app = app
        self.root.title("刷课闹钟 - 状态监控")
        self.root.geometry("400x300")
        self.window_destroyed = False
        
        # 变量
        self.last_time_text = tk.StringVar(value="暂无")
        self.last_duration = tk.StringVar(value="暂无")
        self.next_alarm = tk.StringVar(value="暂无")
        self.status = tk.StringVar(value="就绪")
        
        self.create_widgets()
        self.start_update()
        
        # 绑定窗口关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
    
    def on_close(self):
        """窗口关闭时的回调"""
        self.window_destroyed = True
        self.root.destroy()
    
    def create_widgets(self):
        """创建界面"""
        # 状态指示器
        status_frame = ttk.Frame(self.root)
        status_frame.pack(fill="x", padx=10, pady=10)
        
        ttk.Label(status_frame, text="状态: ").pack(side="left")
        ttk.Label(status_frame, textvariable=self.status, foreground="green", font=("Arial", 10, "bold")).pack(side="left")
        
        # 信息区
        info_frame = ttk.LabelFrame(self.root, text="上次识别", padding=10)
        info_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(info_frame, text="识别结果: ").grid(row=0, column=0, sticky="w")
        ttk.Label(info_frame, textvariable=self.last_time_text).grid(row=0, column=1, sticky="w")
        
        ttk.Label(info_frame, text="视频时长: ").grid(row=1, column=0, sticky="w")
        ttk.Label(info_frame, textvariable=self.last_duration).grid(row=1, column=1, sticky="w")
        
        ttk.Label(info_frame, text="下次提醒: ").grid(row=2, column=0, sticky="w")
        ttk.Label(info_frame, textvariable=self.next_alarm, foreground="red", font=("Arial", 12, "bold")).grid(row=2, column=1, sticky="w")
        
        # 日志区
        log_frame = ttk.LabelFrame(self.root, text="操作日志", padding=10)
        log_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.log_text = tk.Text(log_frame, height=8, wrap="word", state="disabled")
        self.log_text.pack(fill="both", expand=True)
        
        # 按钮区
        button_frame = ttk.Frame(self.root)
        button_frame.pack(fill="x", padx=10, pady=10)
        
        ttk.Button(button_frame, text="生成闹钟", command=self.app.trigger_alarm).pack(side="left", padx=5)
        ttk.Button(button_frame, text="配置", command=self.app.show_config_window).pack(side="left", padx=5)
        ttk.Button(button_frame, text="清空日志", command=self.clear_log).pack(side="right", padx=5)
    
    def add_log(self, message):
        """添加日志 - 线程安全版本"""
        if self.window_destroyed:
            return
        self.root.after(0, self._add_log_unsafe, message)
    
    def _add_log_unsafe(self, message):
        """不安全的添加日志 - 必须在主线程调用"""
        if self.window_destroyed:
            return
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.config(state="normal")
        self.log_text.insert("end", f"[{timestamp}] {message}\n")
        self.log_text.see("end")
        self.log_text.config(state="disabled")
    
    def clear_log(self):
        """清空日志"""
        if self.window_destroyed:
            return
        self.log_text.config(state="normal")
        self.log_text.delete(1.0, "end")
        self.log_text.config(state="disabled")
    
    def update_status(self, status):
        """更新状态 - 线程安全版本"""
        if self.window_destroyed:
            return
        self.root.after(0, self._update_status_unsafe, status)
    
    def _update_status_unsafe(self, status):
        """不安全的更新状态 - 必须在主线程调用"""
        if self.window_destroyed:
            return
        self.status.set(status)
    
    def update_alarm_info(self, time_text: str, duration_minutes: Optional[float]):
        """更新闹钟信息 - 线程安全版本"""
        if self.window_destroyed:
            return
        self.root.after(0, self._update_alarm_info_unsafe, time_text, duration_minutes)
    
    def _update_alarm_info_unsafe(self, time_text: str, duration_minutes: Optional[float]):
        """不安全的更新闹钟信息 - 必须在主线程调用"""
        if self.window_destroyed:
            return
        self.last_time_text.set(time_text)
        
        if duration_minutes:
            if duration_minutes < 60:
                self.last_duration.set(f"{duration_minutes:.1f} 分钟")
            else:
                hours = int(duration_minutes // 60)
                mins = int(duration_minutes % 60)
                self.last_duration.set(f"{hours}小时{mins}分钟")
            
            now = datetime.now()
            alarm_time = now + timedelta(minutes=duration_minutes)
            self.next_alarm.set(alarm_time.strftime("%H:%M:%S"))
        else:
            self.last_duration.set("解析失败")
            self.next_alarm.set("无")
    
    def start_update(self):
        """开始定时更新"""
        self.update_countdown()
    
    def update_countdown(self):
        """更新倒计时"""
        if self.window_destroyed:
            return
        # 简单实现，仅更新状态
        self.root.after(1000, self.update_countdown)


class CourseAlarmGUI:
    """主 GUI 应用"""
    
    def __init__(self):
        self.config_manager = ConfigManager()
        self.config = self.config_manager.get()
        self.app_exit = False
        
        # 创建主根窗口（隐藏）
        self.main_root = tk.Tk()
        self.main_root.withdraw()
        
        # 创建状态窗口
        self.status_root = tk.Toplevel(self.main_root)
        self.status_window = StatusWindow(self.status_root, self)
        
        # 创建托盘
        self.tray = TrayIcon(self)
        
        # 初始化窗口管理器
        from core.window_manager import WindowManager
        self.window_manager = WindowManager()
        
        # 初始化热键监听
        self._init_hotkey_listener()
        
        # 初始化闹钟生成器
        self._init_alarm_generator()
        
        # 绑定主窗口退出
        self.main_root.protocol("WM_DELETE_WINDOW", self.quit)
    
    def _init_hotkey_listener(self):
        """初始化热键监听"""
        try:
            import keyboard
            
            # 绑定 F9 热键
            keyboard.add_hotkey(self.config.hotkey.trigger_key, self.trigger_alarm_safe)
            self.status_window.add_log(f"热键 {self.config.hotkey.trigger_key.upper()} 已绑定")
            
            # 绑定 ESC 热键
            keyboard.add_hotkey(self.config.hotkey.exit_key, self.quit_safe)
            self.status_window.add_log(f"热键 {self.config.hotkey.exit_key.upper()} 已绑定")
            
        except Exception as e:
            self.status_window.add_log(f"热键监听初始化失败: {e}")
    
    def _init_alarm_generator(self):
        """初始化闹钟生成器"""
        try:
            from core.screenshotter import Screenshotter
            from core.ocr_engine import OCREngine
            from core.ics_generator import ICSGenerator
            
            self.screenshotter = Screenshotter()
            self.ocr_engine = OCREngine()
            self.ics_generator = ICSGenerator()
            
            self.status_window.add_log("模块初始化成功")
            
        except Exception as e:
            self.status_window.add_log(f"初始化失败: {e}")
    
    def show_main_window(self):
        """显示主窗口"""
        if not self.app_exit:
            self.status_root.deiconify()
    
    def show_config_window(self):
        """显示配置窗口"""
        if self.app_exit:
            return
        try:
            from gui.config_window import ConfigWindow
            config_root = tk.Toplevel()
            ConfigWindow(config_root, self.config_manager)
            self.status_window.add_log("配置窗口已打开")
        except Exception as e:
            self.status_window.add_log(f"打开配置窗口失败: {e}")
    
    def trigger_alarm_safe(self):
        """安全的触发闹钟生成 - 先检查是否退出再调度到主线程"""
        if self.app_exit:
            return
        self.main_root.after(0, self.trigger_alarm)
    
    def trigger_alarm(self):
        """触发闹钟生成 - 在主线程执行"""
        if self.app_exit:
            return
        
        # 先弹出窗口，让用户能看到过程
        self.status_root.deiconify()
        self.status_root.lift()
        self.status_root.focus_force()
        
        self.status_window.update_status("运行中...")
        self.status_window.add_log("开始生成闹钟...")
        
        try:
            cfg = self.config_manager.get().screenshot
            
            # ====== 第一步：唤醒 Edge 浏览器 ======
            self.status_window.add_log("正在唤醒 Edge 浏览器...")
            edge_hwnd = self.window_manager.find_edge_window()
            
            if edge_hwnd:
                # 强力激活：还原、显示、置顶、设置焦点
                self.window_manager.activate_window(edge_hwnd)
                time.sleep(0.3)
                
                # 调整到右半边
                self.status_window.add_log("正在调整到屏幕右半边...")
                self.window_manager.snap_to_right_half(edge_hwnd, bring_to_front=False)
                time.sleep(0.3)
                
                self.status_window.add_log("Edge 浏览器已就绪！")
            else:
                self.status_window.add_log("警告: 未找到 Edge 浏览器窗口")
            
            # ====== 第二步：触发进度条 ======
            self.status_window.add_log("触发进度条...")
            self.screenshotter.trigger_progress_bar(cfg.start_x, cfg.start_y)
            
            # ====== 第三步：截图 ======
            self.status_window.add_log("截图中...")
            screenshot = self.screenshotter.capture_rectangle(
                cfg.start_x, cfg.start_y,
                cfg.end_x, cfg.end_y
            )
            
            # ====== 第四步：OCR识别 ======
            self.status_window.add_log("OCR识别中...")
            time_text = self.ocr_engine.recognize(screenshot)
            self.status_window.add_log(f"识别结果: {time_text}")
            
            # ====== 第五步：解析时长 ======
            duration_minutes = self.ocr_engine.parse_time(time_text)
            
            if duration_minutes:
                self.status_window.add_log(f"视频时长: {duration_minutes:.1f} 分钟")
                
                # 生成ICS
                self.ics_generator.generate_for_duration(duration_minutes)
                
                self.status_window.update_alarm_info(time_text, duration_minutes)
                self.status_window.add_log("闹钟生成成功！")
            else:
                self.status_window.add_log("时长解析失败！")
                self.status_window.update_alarm_info(time_text, None)
            
        except Exception as e:
            self.status_window.add_log(f"错误: {e}")
            import traceback
            self.status_window.add_log(traceback.format_exc())
        
        self.status_window.update_status("就绪")
        
        # 确保窗口在最前面
        self.status_root.lift()
        self.status_root.focus_force()
    
    def quit_safe(self):
        """安全的退出 - 先检查再调度到主线程"""
        self.main_root.after(0, self.quit)
    
    def quit(self):
        """退出"""
        if self.app_exit:
            return
        self.app_exit = True
        
        try:
            import keyboard
            keyboard.unhook_all()
        except:
            pass
        
        self.tray.stop()
        
        try:
            self.main_root.quit()
        except:
            pass
        
        try:
            self.main_root.destroy()
        except:
            pass
    
    def run(self):
        """运行应用"""
        try:
            self.main_root.mainloop()
        except KeyboardInterrupt:
            self.quit()
        except Exception as e:
            print(f"主循环错误: {e}")


def main():
    """主函数"""
    app = CourseAlarmGUI()
    app.run()


if __name__ == "__main__":
    main()