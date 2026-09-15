# -*- coding: utf-8 -*-
"""
游戏核心逻辑
包含箭头移动、碰撞检测、游戏状态管理
"""

import time
import levels
from levels import EMPTY, UP, DOWN, LEFT, RIGHT


class Arrow:
    """箭头类"""
    def __init__(self, row, col, direction):
        self.row = row
        self.col = col
        self.direction = direction
        self.alive = True
        self.flying = False
        self.fly_progress = 0.0
        self.collision_anim = 0
        self.x = 0  # 屏幕坐标
        self.y = 0
    
    def get_symbol(self):
        """获取方向符号"""
        return levels.DIRECTION_SYMBOLS.get(self.direction, '?')


class GameState:
    """游戏状态"""
    MENU = 0
    PLAYING = 1
    WIN = 2
    LOSE = 3
    LEVEL_COMPLETE = 4


class Game:
    """游戏主类"""
    def __init__(self):
        self.state = GameState.MENU
        self.current_level = 0
        self.grid = []
        self.arrows = []
        self.errors = 0
        self.max_errors = 3
        self.rows = 0
        self.cols = 0
        self.cell_size = 60
        self.board_x = 0
        self.board_y = 0
        self.flying_arrows = []  # 正在飞出的箭头
        
    def load_level(self, level_idx):
        """加载关卡"""
        if level_idx >= len(levels.LEVELS):
            self.state = GameState.WIN
            return False
        
        level_data = levels.LEVELS[level_idx]
        self.current_level = level_idx
        self.grid = [row[:] for row in level_data['grid']]
        self.max_errors = level_data['max_errors']
        self.errors = 0
        self.rows = len(self.grid)
        self.cols = len(self.grid[0]) if self.rows > 0 else 0
        self.state = GameState.PLAYING
        self.flying_arrows = []
        
        # 创建箭头对象
        self.arrows = []
        for r in range(self.rows):
            for c in range(self.cols):
                if self.grid[r][c] != EMPTY:
                    arrow = Arrow(r, c, self.grid[r][c])
                    self.arrows.append(arrow)
        
        return True
    
    def get_remaining_arrows(self):
        """获取剩余箭头数量"""
        return sum(1 for a in self.arrows if a.alive)
    
    def check_path(self, arrow):
        """
        检查箭头前进路径上是否有阻挡
        返回: (可以飞出, 阻挡的箭头列表)
        """
        r, c = arrow.row, arrow.col
        direction = arrow.direction
        blocking_arrows = []
        
        if direction == UP:
            # 向上检查
            for row in range(r - 1, -1, -1):
                if self.grid[row][c] != EMPTY:
                    # 找到阻挡的箭头
                    blocking_arrows.append((row, c))
                    return False, blocking_arrows
            # 没有阻挡，可以飞出
            return True, []
        
        elif direction == DOWN:
            # 向下检查
            for row in range(r + 1, self.rows):
                if self.grid[row][c] != EMPTY:
                    blocking_arrows.append((row, c))
                    return False, blocking_arrows
            return True, []
        
        elif direction == LEFT:
            # 向左检查
            for col in range(c - 1, -1, -1):
                if self.grid[r][col] != EMPTY:
                    blocking_arrows.append((r, col))
                    return False, blocking_arrows
            return True, []
        
        elif direction == RIGHT:
            # 向右检查
            for col in range(c + 1, self.cols):
                if self.grid[r][col] != EMPTY:
                    blocking_arrows.append((r, col))
                    return False, blocking_arrows
            return True, []
        
        return False, []
    
    def click_arrow(self, row, col):
        """
        点击箭头
        返回: (成功消除, 消息)
        """
        if self.state != GameState.PLAYING:
            return False, "游戏未在进行中"
        
        if row < 0 or row >= self.rows or col < 0 or col >= self.cols:
            return False, "点击位置无效"
        
        if self.grid[row][col] == EMPTY:
            return False, "这里没有箭头"
        
        # 找到对应的箭头
        clicked_arrow = None
        for arrow in self.arrows:
            if arrow.row == row and arrow.col == col and arrow.alive:
                clicked_arrow = arrow
                break
        
        if not clicked_arrow:
            return False, "箭头已被消除"
        
        # 检查路径
        can_fly, blocking = self.check_path(clicked_arrow)
        
        if can_fly:
            # 箭头可以飞出
            clicked_arrow.alive = False
            self.grid[row][col] = EMPTY
            clicked_arrow.flying = True
            clicked_arrow.fly_progress = 0.0
            self.flying_arrows.append(clicked_arrow)
            
            # 检查是否通关
            if self.get_remaining_arrows() == 0:
                self.state = GameState.LEVEL_COMPLETE
            
            return True, "箭头飞出！"
        else:
            # 箭头被阻挡
            self.errors += 1
            clicked_arrow.collision_anim = 30  # 碰撞动画帧数
            
            # 检查是否失败
            if self.errors >= self.max_errors:
                self.state = GameState.LOSE
                return False, f"失误次数已用尽！游戏失败"
            
            return False, f"箭头被阻挡！剩余失误: {self.max_errors - self.errors}"
    
    def update(self, dt):
        """更新游戏状态"""
        # 更新飞出动画
        arrows_to_remove = []
        for arrow in self.flying_arrows:
            arrow.fly_progress += dt * 3.0  # 飞出速度
            if arrow.fly_progress >= 1.0:
                arrows_to_remove.append(arrow)
        
        for arrow in arrows_to_remove:
            self.flying_arrows.remove(arrow)
        
        # 更新碰撞动画
        for arrow in self.arrows:
            if arrow.collision_anim > 0:
                arrow.collision_anim -= 1
    
    def next_level(self):
        """进入下一关"""
        if self.state == GameState.LEVEL_COMPLETE:
            self.load_level(self.current_level + 1)
            return True
        return False
    
    def restart_level(self):
        """重新开始当前关卡"""
        self.load_level(self.current_level)
    
    def get_level_name(self):
        """获取当前关卡名称"""
        if self.current_level < len(levels.LEVELS):
            return levels.LEVELS[self.current_level]['name']
        return "未知关卡"
    
    def is_game_complete(self):
        """检查是否通关所有关卡"""
        return self.current_level >= len(levels.LEVELS)
