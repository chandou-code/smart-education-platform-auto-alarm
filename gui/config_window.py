#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
可视化配置界面
"""

# 抑制 libpng iCCP 警告
import warnings
warnings.filterwarnings("ignore", category=UserWarning, message="iCCP")

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import sys

# 添加模块路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.config import ConfigManager


class CoordinateSelector:
    """坐标选择器 - 选择截图区域"""
    
    def __init__(self, parent):
        self.parent = parent
        self.result = None
        self.window = tk.Toplevel(parent)
        self.window.title("选择截图区域")
        self.window.attributes("-fullscreen", True)
        self.window.attributes("-alpha", 0.3)
        self.window.attributes("-topmost", True)
        
        # 画布
        self.canvas = tk.Canvas(self.window, cursor="cross")
        self.canvas.pack(fill="both", expand=True)
        
        # 变量
        self.start_x = None
        self.start_y = None
        self.rect = None
        
        # 绑定事件
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.window.bind("<Escape>", self.cancel)
        
        # 提示
        self.label = tk.Label(
            self.window, 
            text="按住鼠标左键拖动选择区域，按 ESC 取消",
            font=("Arial", 16),
            bg="yellow",
            fg="black"
        )
        self.label.place(relx=0.5, rely=0.02, anchor="n")
    
    def on_click(self, event):
        self.start_x = event.x
        self.start_y = event.y
        self.rect = self.canvas.create_rectangle(
            self.start_x, self.start_y, self.start_x, self.start_y,
            outline="red", width=3, fill="white", stipple="gray25"
        )
    
    def on_drag(self, event):
        if self.rect:
            self.canvas.coords(self.rect, self.start_x, self.start_y, event.x, event.y)
    
    def on_release(self, event):
        self.result = (self.start_x, self.start_y, event.x, event.y)
        self.window.destroy()
    
    def cancel(self, event=None):
        self.result = None
        self.window.destroy()
    
    def show(self):
        self.window.wait_window()
        return self.result


class ConfigWindow:
    """配置窗口"""
    
    def __init__(self, root, config_manager):
        self.root = root
        self.root.title("刷课闹钟 - 配置")
        self.root.geometry("600x700")
        
        self.config_manager = config_manager
        self.config = config_manager.get()
        
        # 变量
        self.var_start_x = tk.IntVar(value=self.config.screenshot.start_x)
        self.var_start_y = tk.IntVar(value=self.config.screenshot.start_y)
        self.var_end_x = tk.IntVar(value=self.config.screenshot.end_x)
        self.var_end_y = tk.IntVar(value=self.config.screenshot.end_y)
        self.var_click_x = tk.IntVar(value=self.config.screenshot.click_x)
        self.var_click_y = tk.IntVar(value=self.config.screenshot.click_y)
        
        self.create_widgets()
    
    def create_widgets(self):
        # 创建标签页
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # 截图配置页
        screenshot_frame = ttk.Frame(notebook)
        notebook.add(screenshot_frame, text="截图配置")
        self.create_screenshot_tab(screenshot_frame)
        
        # OCR配置页
        ocr_frame = ttk.Frame(notebook)
        notebook.add(ocr_frame, text="OCR配置")
        self.create_ocr_tab(ocr_frame)
        
        # 按钮区
        button_frame = ttk.Frame(self.root)
        button_frame.pack(fill="x", padx=10, pady=10)
        
        ttk.Button(button_frame, text="保存配置", command=self.save_config).pack(side="right", padx=5)
        ttk.Button(button_frame, text="重置", command=self.reset_config).pack(side="right", padx=5)
        ttk.Button(button_frame, text="导入配置", command=self.import_config).pack(side="left", padx=5)
        ttk.Button(button_frame, text="导出配置", command=self.export_config).pack(side="left", padx=5)
    
    def create_screenshot_tab(self, parent):
        """创建截图配置页"""
        frame = ttk.LabelFrame(parent, text="坐标配置", padding=10)
        frame.pack(fill="x", padx=10, pady=10)
        
        # 截图区域
        sub_frame1 = ttk.Frame(frame)
        sub_frame1.pack(fill="x", pady=5)
        
        ttk.Label(sub_frame1, text="截图起始坐标:").grid(row=0, column=0, sticky="w")
        ttk.Entry(sub_frame1, textvariable=self.var_start_x, width=10).grid(row=0, column=1, padx=5)
        ttk.Entry(sub_frame1, textvariable=self.var_start_y, width=10).grid(row=0, column=2, padx=5)
        
        ttk.Label(sub_frame1, text="截图结束坐标:").grid(row=1, column=0, sticky="w")
        ttk.Entry(sub_frame1, textvariable=self.var_end_x, width=10).grid(row=1, column=1, padx=5)
        ttk.Entry(sub_frame1, textvariable=self.var_end_y, width=10).grid(row=1, column=2, padx=5)
        
        ttk.Button(sub_frame1, text="选择区域", command=self.select_area).grid(row=0, column=3, rowspan=2, padx=10)
        
        # 点击位置
        sub_frame2 = ttk.Frame(frame)
        sub_frame2.pack(fill="x", pady=10)
        
        ttk.Label(sub_frame2, text="点击位置:").grid(row=0, column=0, sticky="w")
        ttk.Entry(sub_frame2, textvariable=self.var_click_x, width=10).grid(row=0, column=1, padx=5)
        ttk.Entry(sub_frame2, textvariable=self.var_click_y, width=10).grid(row=0, column=2, padx=5)
        
        ttk.Button(sub_frame2, text="选择位置", command=self.select_click).grid(row=0, column=3, padx=10)
        
        # 说明
        info_frame = ttk.LabelFrame(parent, text="使用说明", padding=10)
        info_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        info_text = (
            "1. 点击\"选择区域\"按钮，全屏选择视频时长显示区域\n"
            "2. 点击\"选择位置\"按钮，点击浏览器空白处\n"
            "3. 调整坐标后点击\"保存配置\"\n"
            "4. 可以使用上下左右键微调坐标"
        )
        ttk.Label(info_frame, text=info_text, justify="left").pack(anchor="w")
        
        # 测试按钮
        test_frame = ttk.Frame(parent)
        test_frame.pack(fill="x", padx=10, pady=10)
        ttk.Button(test_frame, text="测试截图", command=self.test_screenshot).pack(fill="x")
    
    def create_ocr_tab(self, parent):
        """创建OCR配置页"""
        # 简单占位，后续完善
        frame = ttk.LabelFrame(parent, text="OCR参数", padding=10)
        frame.pack(fill="x", padx=10, pady=10)
        
        ttk.Label(frame, text="OCR配置功能开发中...").pack()
    
    def select_area(self):
        """选择截图区域"""
        selector = CoordinateSelector(self.root)
        result = selector.show()
        
        if result:
            self.var_start_x.set(result[0])
            self.var_start_y.set(result[1])
            self.var_end_x.set(result[2])
            self.var_end_y.set(result[3])
    
    def select_click(self):
        """选择点击位置"""
        selector = CoordinateSelector(self.root)
        result = selector.show()
        
        if result:
            x = (result[0] + result[2]) // 2
            y = (result[1] + result[3]) // 2
            self.var_click_x.set(x)
            self.var_click_y.set(y)
    
    def test_screenshot(self):
        """测试截图"""
        messagebox.showinfo("提示", "测试功能开发中...")
    
    def save_config(self):
        """保存配置"""
        self.config.screenshot.start_x = self.var_start_x.get()
        self.config.screenshot.start_y = self.var_start_y.get()
        self.config.screenshot.end_x = self.var_end_x.get()
        self.config.screenshot.end_y = self.var_end_y.get()
        self.config.screenshot.click_x = self.var_click_x.get()
        self.config.screenshot.click_y = self.var_click_y.get()
        
        self.config_manager.save_config()
        messagebox.showinfo("成功", "配置已保存!")
    
    def reset_config(self):
        """重置配置"""
        if messagebox.askyesno("确认", "确定要重置所有配置吗?"):
            self.config_manager.config = ConfigManager().config
            self.config = self.config_manager.config
            
            self.var_start_x.set(self.config.screenshot.start_x)
            self.var_start_y.set(self.config.screenshot.start_y)
            self.var_end_x.set(self.config.screenshot.end_x)
            self.var_end_y.set(self.config.screenshot.end_y)
            self.var_click_x.set(self.config.screenshot.click_x)
            self.var_click_y.set(self.config.screenshot.click_y)
    
    def import_config(self):
        """导入配置"""
        filename = filedialog.askopenfilename(
            title="导入配置",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            self.config_manager = ConfigManager(filename)
            self.config = self.config_manager.get()
            
            self.var_start_x.set(self.config.screenshot.start_x)
            self.var_start_y.set(self.config.screenshot.start_y)
            self.var_end_x.set(self.config.screenshot.end_x)
            self.var_end_y.set(self.config.screenshot.end_y)
            self.var_click_x.set(self.config.screenshot.click_x)
            self.var_click_y.set(self.config.screenshot.click_y)
            
            messagebox.showinfo("成功", "配置已导入!")
    
    def export_config(self):
        """导出配置"""
        filename = filedialog.asksaveasfilename(
            title="导出配置",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            import shutil
            shutil.copy(self.config_manager.config_path, filename)
            messagebox.showinfo("成功", "配置已导出!")


def main():
    """主函数"""
    config_manager = ConfigManager()
    
    root = tk.Tk()
    app = ConfigWindow(root, config_manager)
    root.mainloop()


if __name__ == "__main__":
    main()