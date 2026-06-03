#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
截图模块
负责屏幕截图和鼠标操作
"""

import pyautogui
import time
from PIL import Image
from typing import Tuple, Optional


class Screenshotter:
    """截图器"""
    
    def __init__(self):
        pass
    
    def click(self, x: int, y: int):
        """点击指定位置"""
        pyautogui.click(x, y)
    
    def move_to(self, x: int, y: int, duration: float = 0):
        """移动鼠标到指定位置"""
        pyautogui.moveTo(x, y, duration=duration)
    
    def trigger_progress_bar(self, x: int, y: int):
        """移动鼠标并触发进度条显示
        
        移动到目标位置后，上下左右各移动3像素，最后回到原点
        """
        pyautogui.moveTo(x, y, duration=0)
        pyautogui.moveRel(3, 0, duration=0)    # 右移3像素
        pyautogui.moveRel(-6, 0, duration=0)   # 左移6像素（回到原点再左移3像素）
        pyautogui.moveRel(3, 3, duration=0)    # 右移3像素，下移3像素
        pyautogui.moveRel(0, -6, duration=0)   # 上移6像素
        pyautogui.moveRel(0, 3, duration=0)    # 下移3像素，回到原点
    
    def capture_rectangle(self, x1: int, y1: int, x2: int, y2: int) -> Image.Image:
        """截取矩形区域
        
        Args:
            x1, y1: 起始坐标
            x2, y2: 结束坐标
        
        Returns:
            PIL.Image: 截取的图像
        """
        left = min(x1, x2)
        top = min(y1, y2)
        right = max(x1, x2)
        bottom = max(y1, y2)
        
        from PIL import ImageGrab
        screenshot = ImageGrab.grab(bbox=(left, top, right, bottom))
        return screenshot
    
    def capture_with_trigger(
        self,
        start_x: int,
        start_y: int,
        end_x: int,
        end_y: int,
        click_pos: Optional[Tuple[int, int]] = None
    ) -> Image.Image:
        """完整截图流程
        
        Args:
            start_x, start_y: 截图起始坐标
            end_x, end_y: 截图结束坐标
            click_pos: 点击位置（可选）
        
        Returns:
            PIL.Image: 截取的图像
        """
        # 如果需要点击
        if click_pos:
            self.click(click_pos[0], click_pos[1])
            time.sleep(0.5)
        
        # 触发进度条显示
        self.trigger_progress_bar(start_x, start_y)
        
        # 截图
        return self.capture_rectangle(start_x, start_y, end_x, end_y)