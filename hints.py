# -*- coding: utf-8 -*-
"""
提示系统模块
帮助玩家找到可点击的箭头
"""

from game import Game
from levels import EMPTY


class HintSystem:
    """提示系统"""
    def __init__(self, game):
        self.game = game
        self.hint_arrow = None
        self.hint_timer = 0
        self.hint_duration = 60  # 提示显示帧数
    
    def find_clickable_arrow(self):
        """找到一个可以点击的箭头"""
        for arrow in self.game.arrows:
            if not arrow.alive:
                continue
            can_fly, _ = self.game.check_path(arrow)
            if can_fly:
                return arrow
        return None
    
    def show_hint(self):
        """显示提示"""
        self.hint_arrow = self.find_clickable_arrow()
        if self.hint_arrow:
            self.hint_timer = self.hint_duration
            return True
        return False
    
    def update(self):
        """更新提示状态"""
        if self.hint_timer > 0:
            self.hint_timer -= 1
            if self.hint_timer <= 0:
                self.hint_arrow = None
    
    def get_hint_arrow(self):
        """获取当前提示的箭头"""
        return self.hint_arrow if self.hint_timer > 0 else None
    
    def is_hint_active(self):
        """检查提示是否激活"""
        return self.hint_timer > 0
