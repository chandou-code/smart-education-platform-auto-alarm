#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
窗口管理模块
负责控制浏览器窗口的位置和大小
"""

import ctypes
from ctypes import wintypes
from typing import Optional, Tuple


class WindowManager:
    """窗口管理器"""
    
    def __init__(self):
        self.user32 = ctypes.windll.user32
        self.kernel32 = ctypes.windll.kernel32
        
        # 定义Windows API函数
        self.user32.EnumWindows.restype = wintypes.BOOL
        self.user32.EnumWindows.argtypes = [
            ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM),
            wintypes.LPARAM
        ]
        
        self.user32.GetWindowTextLengthW.restype = ctypes.c_int
        self.user32.GetWindowTextLengthW.argtypes = [wintypes.HWND]
        
        self.user32.GetWindowTextW.restype = ctypes.c_int
        self.user32.GetWindowTextW.argtypes = [
            wintypes.HWND,
            wintypes.LPWSTR,
            ctypes.c_int
        ]
        
        self.user32.SetWindowPos.restype = wintypes.BOOL
        self.user32.SetWindowPos.argtypes = [
            wintypes.HWND,
            wintypes.HWND,
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_uint
        ]
        
        self.user32.GetWindowRect.restype = wintypes.BOOL
        self.user32.GetWindowRect.argtypes = [
            wintypes.HWND,
            ctypes.POINTER(wintypes.RECT)
        ]
        
        self.user32.IsWindowVisible.restype = wintypes.BOOL
        self.user32.IsWindowVisible.argtypes = [wintypes.HWND]
        
        self.user32.SetForegroundWindow.restype = wintypes.BOOL
        self.user32.SetForegroundWindow.argtypes = [wintypes.HWND]
        
        self.user32.ShowWindow.restype = wintypes.BOOL
        self.user32.ShowWindow.argtypes = [wintypes.HWND, ctypes.c_int]
        
        self.user32.IsIconic.restype = wintypes.BOOL
        self.user32.IsIconic.argtypes = [wintypes.HWND]
        
        self.user32.SetFocus.restype = wintypes.HWND
        self.user32.SetFocus.argtypes = [wintypes.HWND]
        
        # 窗口定位标志
        self.SWP_NOZORDER = 0x0004
        self.SWP_SHOWWINDOW = 0x0040
        self.SW_RESTORE = 9
        self.SW_SHOW = 5
        
        # 窗口句柄缓存
        self._cached_edge_hwnd = None
        self._all_edge_windows = []
    
    def _enum_windows_callback(self, hwnd: wintypes.HWND, _: wintypes.LPARAM) -> bool:
        """枚举窗口回调函数"""
        # 检查窗口是否可见
        if not self.user32.IsWindowVisible(hwnd):
            return True  # 继续枚举
        
        length = self.user32.GetWindowTextLengthW(hwnd)
        if length > 0:
            buffer = ctypes.create_unicode_buffer(length + 1)
            self.user32.GetWindowTextW(hwnd, buffer, length + 1)
            window_title = buffer.value
            if self._is_edge_window(window_title):
                # 获取窗口位置信息
                rect = wintypes.RECT()
                self.user32.GetWindowRect(hwnd, ctypes.byref(rect))
                
                self._all_edge_windows.append({
                    'hwnd': hwnd,
                    'title': window_title,
                    'left': rect.left,
                    'top': rect.top,
                    'right': rect.right,
                    'bottom': rect.bottom,
                    'width': rect.right - rect.left,
                    'height': rect.bottom - rect.top
                })
                
                # 如果还没有缓存第一个窗口，就缓存它
                if self._cached_edge_hwnd is None:
                    self._cached_edge_hwnd = hwnd
        return True  # 继续枚举所有窗口
    
    def _is_edge_window(self, title: str) -> bool:
        """判断是否是Edge浏览器窗口"""
        return ("Microsoft Edge" in title) or ("Edge" in title and "Microsoft" in title)
    
    def find_edge_window(self) -> Optional[int]:
        """查找Edge浏览器窗口（第一个找到的）
        
        Returns:
            窗口句柄，未找到返回None
        """
        self._cached_edge_hwnd = None
        self._all_edge_windows = []
        enum_proc = ctypes.WINFUNCTYPE(
            wintypes.BOOL, wintypes.HWND, wintypes.LPARAM
        )(self._enum_windows_callback)
        self.user32.EnumWindows(enum_proc, 0)
        return self._cached_edge_hwnd
    
    def find_all_edge_windows(self) -> list:
        """查找所有可见的Edge浏览器窗口
        
        Returns:
            窗口信息列表，每个元素是一个字典，包含：
            - hwnd: 窗口句柄
            - title: 窗口标题
            - left, top, right, bottom: 窗口位置
            - width, height: 窗口大小
        """
        self._cached_edge_hwnd = None
        self._all_edge_windows = []
        enum_proc = ctypes.WINFUNCTYPE(
            wintypes.BOOL, wintypes.HWND, wintypes.LPARAM
        )(self._enum_windows_callback)
        self.user32.EnumWindows(enum_proc, 0)
        return self._all_edge_windows
    
    def print_edge_windows(self):
        """打印所有Edge窗口信息"""
        windows = self.find_all_edge_windows()
        if not windows:
            print("未找到任何Edge浏览器窗口")
            return
        
        print(f"找到 {len(windows)} 个Edge窗口:")
        print("-" * 80)
        for i, win in enumerate(windows):
            print(f"[{i}] 句柄: {win['hwnd']}")
            print(f"    标题: {win['title']}")
            print(f"    位置: ({win['left']}, {win['top']})")
            print(f"    大小: {win['width']}x{win['height']}")
            print("-" * 80)
    
    def set_foreground_window(self, hwnd: int) -> bool:
        """将窗口设置为前台窗口
        
        Args:
            hwnd: 窗口句柄
            
        Returns:
            是否成功
        """
        return bool(self.user32.SetForegroundWindow(hwnd))
    
    def activate_window(self, hwnd: int) -> bool:
        """强力激活窗口（还原+置顶+设置焦点）
        
        Args:
            hwnd: 窗口句柄
            
        Returns:
            是否成功
        """
        # 1. 如果窗口是最小化的，先还原
        if bool(self.user32.IsIconic(hwnd)):
            self.user32.ShowWindow(hwnd, self.SW_RESTORE)
        
        # 2. 显示窗口
        self.user32.ShowWindow(hwnd, self.SW_SHOW)
        
        # 3. 置顶窗口
        success = bool(self.user32.SetForegroundWindow(hwnd))
        
        # 4. 设置焦点
        if success:
            self.user32.SetFocus(hwnd)
            
            # 5. 额外：再次确保在最前面
            self.user32.SetWindowPos(
                hwnd,
                -1,  # HWND_TOPMOST
                0, 0, 0, 0,
                0x0003  # SWP_NOMOVE | SWP_NOSIZE
            )
        
        return success
    
    def resize_and_move(
        self,
        hwnd: int,
        x: int,
        y: int,
        width: int,
        height: int,
        insert_after: Optional[int] = None,
        bring_to_front: bool = True
    ) -> bool:
        """调整任意窗口大小并移动位置
        
        Args:
            hwnd: 窗口句柄
            x: 新的X坐标
            y: 新的Y坐标
            width: 新的宽度
            height: 新的高度
            insert_after: 插入到哪个窗口后面，可选
            bring_to_front: 是否将窗口置于前台
            
        Returns:
            是否成功
        """
        if bring_to_front:
            self.set_foreground_window(hwnd)
        
        return self.set_window_pos(hwnd, x, y, width, height, insert_after)
    
    def get_window_rect(self, hwnd: int) -> Optional[Tuple[int, int, int, int]]:
        """获取窗口位置和大小
        
        Args:
            hwnd: 窗口句柄
            
        Returns:
            (left, top, right, bottom)，失败返回None
        """
        rect = wintypes.RECT()
        if self.user32.GetWindowRect(hwnd, ctypes.byref(rect)):
            return (rect.left, rect.top, rect.right, rect.bottom)
        return None
    
    def set_window_pos(
        self,
        hwnd: int,
        x: int,
        y: int,
        width: int,
        height: int,
        insert_after: Optional[int] = None
    ) -> bool:
        """设置窗口位置和大小
        
        Args:
            hwnd: 窗口句柄
            x: X坐标
            y: Y坐标
            width: 宽度
            height: 高度
            insert_after: 插入到哪个窗口后面，可选
            
        Returns:
            是否成功
        """
        if insert_after is None:
            insert_after = 0
        
        return bool(self.user32.SetWindowPos(
            hwnd,
            insert_after,
            x,
            y,
            width,
            height,
            self.SWP_NOZORDER | self.SWP_SHOWWINDOW
        ))
    
    def resize_and_move_edge(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        use_cache: bool = True
    ) -> bool:
        """调整Edge窗口大小并移动位置
        
        Args:
            x: 新的X坐标
            y: 新的Y坐标
            width: 新的宽度
            height: 新的高度
            use_cache: 是否使用缓存的窗口句柄
            
        Returns:
            是否成功
        """
        hwnd = None
        if use_cache and self._cached_edge_hwnd is not None:
            hwnd = self._cached_edge_hwnd
        
        if hwnd is None:
            hwnd = self.find_edge_window()
        
        if hwnd is None:
            print("错误: 未找到Edge浏览器窗口")
            return False
        
        success = self.set_window_pos(hwnd, x, y, width, height)
        if success:
            print(f"成功调整Edge窗口: 位置({x}, {y})，大小{width}x{height}")
        else:
            print("错误: 调整窗口失败")
        
        return success
    
    def get_screen_size(self) -> Tuple[int, int]:
        """获取屏幕分辨率
        
        Returns:
            (width, height)
        """
        width = self.user32.GetSystemMetrics(0)
        height = self.user32.GetSystemMetrics(1)
        return (width, height)
    
    def snap_to_left_half(self, hwnd: int, bring_to_front: bool = True) -> bool:
        """将窗口吸附到屏幕左半边
        
        Args:
            hwnd: 窗口句柄
            bring_to_front: 是否将窗口置于前台
            
        Returns:
            是否成功
        """
        screen_width, screen_height = self.get_screen_size()
        half_width = screen_width // 2
        return self.resize_and_move(
            hwnd=hwnd,
            x=0,
            y=0,
            width=half_width,
            height=screen_height,
            bring_to_front=bring_to_front
        )
    
    def snap_to_right_half(self, hwnd: int, bring_to_front: bool = True) -> bool:
        """将窗口吸附到屏幕右半边
        
        Args:
            hwnd: 窗口句柄
            bring_to_front: 是否将窗口置于前台
            
        Returns:
            是否成功
        """
        screen_width, screen_height = self.get_screen_size()
        half_width = screen_width // 2
        return self.resize_and_move(
            hwnd=hwnd,
            x=half_width,
            y=0,
            width=half_width,
            height=screen_height,
            bring_to_front=bring_to_front
        )
    
    def snap_to_top_half(self, hwnd: int, bring_to_front: bool = True) -> bool:
        """将窗口吸附到屏幕上半边
        
        Args:
            hwnd: 窗口句柄
            bring_to_front: 是否将窗口置于前台
            
        Returns:
            是否成功
        """
        screen_width, screen_height = self.get_screen_size()
        half_height = screen_height // 2
        return self.resize_and_move(
            hwnd=hwnd,
            x=0,
            y=0,
            width=screen_width,
            height=half_height,
            bring_to_front=bring_to_front
        )
    
    def snap_to_bottom_half(self, hwnd: int, bring_to_front: bool = True) -> bool:
        """将窗口吸附到屏幕下半边
        
        Args:
            hwnd: 窗口句柄
            bring_to_front: 是否将窗口置于前台
            
        Returns:
            是否成功
        """
        screen_width, screen_height = self.get_screen_size()
        half_height = screen_height // 2
        return self.resize_and_move(
            hwnd=hwnd,
            x=0,
            y=half_height,
            width=screen_width,
            height=half_height,
            bring_to_front=bring_to_front
        )
    
    def snap_to_top_left(self, hwnd: int, bring_to_front: bool = True) -> bool:
        """将窗口吸附到屏幕左上四分之一
        
        Args:
            hwnd: 窗口句柄
            bring_to_front: 是否将窗口置于前台
            
        Returns:
            是否成功
        """
        screen_width, screen_height = self.get_screen_size()
        half_width = screen_width // 2
        half_height = screen_height // 2
        return self.resize_and_move(
            hwnd=hwnd,
            x=0,
            y=0,
            width=half_width,
            height=half_height,
            bring_to_front=bring_to_front
        )
    
    def snap_to_top_right(self, hwnd: int, bring_to_front: bool = True) -> bool:
        """将窗口吸附到屏幕右上四分之一
        
        Args:
            hwnd: 窗口句柄
            bring_to_front: 是否将窗口置于前台
            
        Returns:
            是否成功
        """
        screen_width, screen_height = self.get_screen_size()
        half_width = screen_width // 2
        half_height = screen_height // 2
        return self.resize_and_move(
            hwnd=hwnd,
            x=half_width,
            y=0,
            width=half_width,
            height=half_height,
            bring_to_front=bring_to_front
        )
    
    def snap_to_bottom_left(self, hwnd: int, bring_to_front: bool = True) -> bool:
        """将窗口吸附到屏幕左下四分之一
        
        Args:
            hwnd: 窗口句柄
            bring_to_front: 是否将窗口置于前台
            
        Returns:
            是否成功
        """
        screen_width, screen_height = self.get_screen_size()
        half_width = screen_width // 2
        half_height = screen_height // 2
        return self.resize_and_move(
            hwnd=hwnd,
            x=0,
            y=half_height,
            width=half_width,
            height=half_height,
            bring_to_front=bring_to_front
        )
    
    def snap_to_bottom_right(self, hwnd: int, bring_to_front: bool = True) -> bool:
        """将窗口吸附到屏幕右下四分之一
        
        Args:
            hwnd: 窗口句柄
            bring_to_front: 是否将窗口置于前台
            
        Returns:
            是否成功
        """
        screen_width, screen_height = self.get_screen_size()
        half_width = screen_width // 2
        half_height = screen_height // 2
        return self.resize_and_move(
            hwnd=hwnd,
            x=half_width,
            y=half_height,
            width=half_width,
            height=half_height,
            bring_to_front=bring_to_front
        )