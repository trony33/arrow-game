# -*- coding: utf-8 -*-
"""
生成游戏截图脚本
用于生成游戏界面截图
"""

import pygame
import sys
import os

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import ArrowGameApp, WINDOW_WIDTH, WINDOW_HEIGHT
from game import GameState


def take_screenshot(app, filename):
    """截取当前画面"""
    pygame.image.save(app.screen, filename)
    print(f"截图已保存: {filename}")


def main():
    """生成截图"""
    pygame.init()
    
    # 创建游戏实例
    app = ArrowGameApp()
    
    # 创建截图目录
    screenshots_dir = os.path.join(os.path.dirname(__file__), "screenshots")
    os.makedirs(screenshots_dir, exist_ok=True)
    
    # 截取主菜单
    app.draw()
    take_screenshot(app, os.path.join(screenshots_dir, "01_menu.png"))
    
    # 开始游戏
    app.game.load_level(0)
    app.hint_system = None  # 简化处理
    app.draw()
    take_screenshot(app, os.path.join(screenshots_dir, "02_game.png"))
    
    # 模拟点击一个箭头
    for arrow in app.game.arrows:
        if arrow.alive:
            can_fly, _ = app.game.check_path(arrow)
            if can_fly:
                app.game.click_arrow(arrow.row, arrow.col)
                app.draw()
                take_screenshot(app, os.path.join(screenshots_dir, "03_arrow_fly.png"))
                break
    
    # 重新开始
    app.game.restart_level()
    app.draw()
    take_screenshot(app, os.path.join(screenshots_dir, "04_restart.png"))
    
    pygame.quit()
    print("\n所有截图已生成完毕！")


if __name__ == "__main__":
    main()
