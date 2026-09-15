# -*- coding: utf-8 -*-
"""
游戏运行脚本
用于启动游戏并可选地截取截图
"""

import sys
import os

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import main

if __name__ == "__main__":
    print("=" * 50)
    print("一箭又一箭 - Arrow by Arrow")
    print("=" * 50)
    print()
    print("操作说明:")
    print("  - 鼠标左键: 点击箭头")
    print("  - R键: 重新开始当前关卡")
    print("  - H键: 显示提示")
    print("  - M键: 静音/开启音效")
    print("  - ESC键: 返回主菜单/退出游戏")
    print()
    print("正在启动游戏...")
    print()
    
    try:
        main()
    except KeyboardInterrupt:
        print("\n游戏已退出")
    except Exception as e:
        print(f"\n游戏出错: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
