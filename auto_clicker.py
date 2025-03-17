import cv2
import numpy as np
import pyautogui
import time
import os
import sys
from datetime import datetime

class AutoClicker:
    def __init__(self, template_path, interval=30, threshold=0.8):
        """
        初始化自动点击器
        
        参数:
            template_path: 模板图像的路径
            interval: 截图间隔时间(秒)
            threshold: 模板匹配的阈值，越高要求越精确
        """
        self.interval = interval
        self.threshold = threshold
        
        # 加载模板图像
        if not os.path.exists(template_path):
            print(f"错误: 模板图像 '{template_path}' 不存在")
            sys.exit(1)
            
        self.template = cv2.imread(template_path)
        if self.template is None:
            print(f"错误: 无法加载模板图像 '{template_path}'")
            sys.exit(1)
            
        # 转换模板为灰度图
        self.template_gray = cv2.cvtColor(self.template, cv2.COLOR_BGR2GRAY)
        self.template_w, self.template_h = self.template_gray.shape[::-1]
        
        print(f"已加载模板图像，尺寸: {self.template_w}x{self.template_h}")
        print(f"将每 {self.interval} 秒执行一次截图和匹配操作")
        
    def take_screenshot(self):
        """
        截取屏幕并返回图像
        """
        screenshot = pyautogui.screenshot()
        # 转换为OpenCV格式
        screenshot = np.array(screenshot)
        screenshot = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)
        return screenshot
    
    def find_and_click(self):
        """
        截图，查找模板，并点击匹配位置
        
        返回:
            bool: 是否找到并点击了匹配项
        """
        # 截取屏幕
        screenshot = self.take_screenshot()
        screenshot_gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
        
        # 使用模板匹配
        result = cv2.matchTemplate(screenshot_gray, self.template_gray, cv2.TM_CCOEFF_NORMED)
        
        # 查找匹配位置
        locations = np.where(result >= self.threshold)
        
        if len(locations[0]) > 0:
            # 获取第一个匹配位置
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            top_left = max_loc
            
            # 计算点击位置（模板中心）
            click_x = top_left[0] + self.template_w // 2
            click_y = top_left[1] + self.template_h // 2
            
            # 模拟点击
            pyautogui.click(click_x, click_y)
            
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{timestamp}] 找到匹配! 点击位置: ({click_x}, {click_y})")
            
            # 保存匹配结果（可选）
            # self.save_match_result(screenshot, top_left)
            
            return True
        else:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{timestamp}] 未找到匹配")
            return False
    
    def save_match_result(self, screenshot, top_left):
        """
        保存匹配结果的可视化图像（调试用）
        """
        # 创建结果目录
        if not os.path.exists("results"):
            os.makedirs("results")
            
        # 在截图上绘制矩形标记匹配位置
        result_img = screenshot.copy()
        bottom_right = (top_left[0] + self.template_w, top_left[1] + self.template_h)
        cv2.rectangle(result_img, top_left, bottom_right, (0, 255, 0), 2)
        
        # 保存结果
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        result_path = f"results/match_{timestamp}.png"
        cv2.imwrite(result_path, result_img)
        print(f"已保存匹配结果: {result_path}")
    
    def run(self):
        """
        运行自动点击器
        """
        print("自动点击器已启动，按 Ctrl+C 停止...")
        try:
            while True:
                self.find_and_click()
                time.sleep(self.interval)
        except KeyboardInterrupt:
            print("\n自动点击器已停止")

def main():
    # 检查命令行参数
    if len(sys.argv) < 2:
        print("用法: python auto_clicker.py <模板图像路径> [间隔时间(秒)]")
        print("例如: python auto_clicker.py template.png 30")
        sys.exit(1)
    
    # 获取参数
    template_path = sys.argv[1]
    interval = 30  # 默认30秒
    
    if len(sys.argv) >= 3:
        try:
            interval = int(sys.argv[2])
        except ValueError:
            print(f"错误: 间隔时间必须是整数，使用默认值 {interval} 秒")
    
    # 创建并运行自动点击器
    clicker = AutoClicker(template_path, interval)
    clicker.run()

if __name__ == "__main__":
    main()