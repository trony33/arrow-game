# -*- coding: utf-8 -*-
"""
一箭又一箭 - 主程序
使用 Pygame 实现图形界面
"""

import pygame
import sys
import math
from game import Game, GameState
from levels import EMPTY, UP, DOWN, LEFT, RIGHT
from sounds import get_sound_manager
from hints import HintSystem

# 初始化 Pygame
pygame.init()

# 颜色定义
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
DARK_GRAY = (100, 100, 100)
RED = (220, 50, 50)
GREEN = (50, 180, 50)
BLUE = (50, 100, 220)
YELLOW = (220, 180, 50)
ORANGE = (220, 130, 50)
LIGHT_BLUE = (173, 216, 230)
LIGHT_GREEN = (144, 238, 144)
LIGHT_RED = (255, 182, 193)
BG_COLOR = (240, 240, 245)
BOARD_BG = (255, 255, 255)
CELL_BORDER = (180, 180, 190)

# 窗口尺寸
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600

# 箭头颜色
ARROW_COLORS = {
    UP: BLUE,
    DOWN: GREEN,
    LEFT: ORANGE,
    RIGHT: RED,
}


def draw_arrow(surface, x, y, size, direction, color, alpha=255):
    """绘制箭头"""
    half = size // 2
    center_x = x + half
    center_y = y + half
    
    # 创建临时surface用于透明度
    arrow_surface = pygame.Surface((size, size), pygame.SRCALPHA)
    
    if direction == UP:
        points = [
            (half, 5),           # 顶部
            (size - 10, half - 5),  # 右下
            (half + 8, half - 5),   # 右中
            (half + 8, size - 10),  # 右底
            (half - 8, size - 10),  # 左底
            (half - 8, half - 5),   # 左中
            (10, half - 5),      # 左下
        ]
    elif direction == DOWN:
        points = [
            (half, size - 5),   # 底部
            (size - 10, half + 5),  # 右上
            (half + 8, half + 5),   # 右中
            (half + 8, 10),     # 右顶
            (half - 8, 10),     # 左顶
            (half - 8, half + 5),   # 左中
            (10, half + 5),     # 左上
        ]
    elif direction == LEFT:
        points = [
            (5, half),           # 左侧
            (half - 5, 10),      # 上右
            (half - 5, half - 8),  # 上中
            (size - 10, half - 8), # 上底
            (size - 10, half + 8), # 下底
            (half - 5, half + 8),  # 下中
            (half - 5, size - 10), # 下右
        ]
    elif direction == RIGHT:
        points = [
            (size - 5, half),    # 右侧
            (half + 5, 10),      # 上左
            (half + 5, half - 8),  # 上中
            (10, half - 8),      # 上顶
            (10, half + 8),      # 下顶
            (half + 5, half + 8),  # 下中
            (half + 5, size - 10), # 下左
        ]
    
    color_with_alpha = (*color[:3], alpha)
    pygame.draw.polygon(arrow_surface, color_with_alpha, points)
    surface.blit(arrow_surface, (x, y))


def draw_text_centered(surface, text, font, color, x, y):
    """绘制居中文字"""
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(x, y))
    surface.blit(text_surface, text_rect)


def draw_button(surface, text, font, x, y, width, height, color, hover=False):
    """绘制按钮"""
    btn_color = (min(color[0] + 30, 255), min(color[1] + 30, 255), min(color[2] + 30, 255)) if hover else color
    pygame.draw.rect(surface, btn_color, (x, y, width, height), border_radius=8)
    pygame.draw.rect(surface, BLACK, (x, y, width, height), 2, border_radius=8)
    draw_text_centered(surface, text, font, WHITE, x + width // 2, y + height // 2)


class ArrowGameApp:
    """游戏应用主类"""
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("一箭又一箭 - Arrow by Arrow")
        self.clock = pygame.time.Clock()
        
        # 字体
        self.font_large = pygame.font.SysFont("Microsoft YaHei", 48, bold=True)
        self.font_medium = pygame.font.SysFont("Microsoft YaHei", 32)
        self.font_small = pygame.font.SysFont("Microsoft YaHei", 24)
        self.font_tiny = pygame.font.SysFont("Microsoft YaHei", 18)
        
        # 游戏实例
        self.game = Game()
        
        # 音效管理器
        self.sound_manager = get_sound_manager()
        
        # 提示系统
        self.hint_system = None
        
        # 状态
        self.running = True
        self.mouse_pos = (0, 0)
        self.hovered_arrow = None
        
    def run(self):
        """主循环"""
        while self.running:
            dt = self.clock.tick(60) / 1000.0  # 60 FPS
            self.handle_events()
            self.update(dt)
            self.draw()
        
        pygame.quit()
        sys.exit()
    
    def handle_events(self):
        """处理事件"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.game.state == GameState.MENU:
                        self.running = False
                    else:
                        self.game.state = GameState.MENU
                
                elif event.key == pygame.K_r:
                    if self.game.state in [GameState.PLAYING, GameState.LOSE]:
                        self.game.restart_level()
                
                elif event.key == pygame.K_h:
                    if self.game.state == GameState.PLAYING and self.hint_system:
                        self.hint_system.show_hint()
                
                elif event.key == pygame.K_m:
                    self.sound_manager.toggle()
            
            elif event.type == pygame.MOUSEMOTION:
                self.mouse_pos = event.pos
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # 左键点击
                    self.handle_click(event.pos)
    
    def handle_click(self, pos):
        """处理鼠标点击"""
        x, y = pos
        
        if self.game.state == GameState.MENU:
            # 开始按钮
            btn_x = WINDOW_WIDTH // 2 - 100
            btn_y = 350
            if btn_x <= x <= btn_x + 200 and btn_y <= y <= btn_y + 50:
                self.game.load_level(0)
                self.hint_system = HintSystem(self.game)
        
        elif self.game.state == GameState.PLAYING:
            # 检查是否点击了重新开始按钮
            btn_x = WINDOW_WIDTH - 150
            btn_y = 20
            if btn_x <= x <= btn_x + 120 and btn_y <= y <= btn_y + 40:
                self.game.restart_level()
                return
            
            # 检查是否点击了提示按钮
            btn_x2 = WINDOW_WIDTH - 150
            btn_y2 = 70
            if btn_x2 <= x <= btn_x2 + 120 and btn_y2 <= y <= btn_y2 + 40:
                if self.hint_system:
                    self.hint_system.show_hint()
                return
            
            # 检查是否点击了静音按钮
            btn_x3 = WINDOW_WIDTH - 150
            btn_y3 = 120
            if btn_x3 <= x <= btn_x3 + 120 and btn_y3 <= y <= btn_y3 + 40:
                self.sound_manager.toggle()
                return
            
            # 检查是否点击了棋盘
            board_x = self.game.board_x
            board_y = self.game.board_y
            cell_size = self.game.cell_size
            
            for arrow in self.game.arrows:
                if not arrow.alive:
                    continue
                ax = board_x + arrow.col * cell_size
                ay = board_y + arrow.row * cell_size
                if ax <= x <= ax + cell_size and ay <= y <= ay + cell_size:
                    result, msg = self.game.click_arrow(arrow.row, arrow.col)
                    if result:
                        self.sound_manager.play('fly')
                    else:
                        self.sound_manager.play('collision')
                    break
        
        elif self.game.state == GameState.LEVEL_COMPLETE:
            # 下一关按钮
            btn_x = WINDOW_WIDTH // 2 - 100
            btn_y = 400
            if btn_x <= x <= btn_x + 200 and btn_y <= y <= btn_y + 50:
                self.sound_manager.play('click')
                if not self.game.next_level():
                    self.game.state = GameState.WIN
        
        elif self.game.state == GameState.LOSE:
            # 重新开始按钮
            btn_x = WINDOW_WIDTH // 2 - 100
            btn_y = 400
            if btn_x <= x <= btn_x + 200 and btn_y <= y <= btn_y + 50:
                self.sound_manager.play('click')
                self.game.restart_level()
        
        elif self.game.state == GameState.WIN:
            # 返回主菜单按钮
            btn_x = WINDOW_WIDTH // 2 - 100
            btn_y = 400
            if btn_x <= x <= btn_x + 200 and btn_y <= y <= btn_y + 50:
                self.sound_manager.play('click')
                self.game.state = GameState.MENU
    
    def update(self, dt):
        """更新游戏状态"""
        # 记录之前的状态
        prev_state = self.game.state
        
        self.game.update(dt)
        
        # 更新提示系统
        if self.hint_system:
            self.hint_system.update()
        
        # 检测状态变化并播放音效
        if prev_state != self.game.state:
            if self.game.state == GameState.LEVEL_COMPLETE:
                self.sound_manager.play('win')
            elif self.game.state == GameState.LOSE:
                self.sound_manager.play('lose')
        
        # 更新悬停状态
        self.hovered_arrow = None
        if self.game.state == GameState.PLAYING:
            x, y = self.mouse_pos
            board_x = self.game.board_x
            board_y = self.game.board_y
            cell_size = self.game.cell_size
            
            for arrow in self.game.arrows:
                if not arrow.alive:
                    continue
                ax = board_x + arrow.col * cell_size
                ay = board_y + arrow.row * cell_size
                if ax <= x <= ax + cell_size and ay <= y <= ay + cell_size:
                    self.hovered_arrow = arrow
                    break
    
    def draw(self):
        """绘制画面"""
        self.screen.fill(BG_COLOR)
        
        if self.game.state == GameState.MENU:
            self.draw_menu()
        elif self.game.state == GameState.PLAYING:
            self.draw_game()
        elif self.game.state == GameState.LEVEL_COMPLETE:
            self.draw_level_complete()
        elif self.game.state == GameState.LOSE:
            self.draw_lose()
        elif self.game.state == GameState.WIN:
            self.draw_win()
        
        pygame.display.flip()
    
    def draw_menu(self):
        """绘制开始菜单"""
        # 标题
        draw_text_centered(self.screen, "一箭又一箭", self.font_large, BLACK, 
                          WINDOW_WIDTH // 2, 150)
        draw_text_centered(self.screen, "Arrow by Arrow", self.font_medium, DARK_GRAY, 
                          WINDOW_WIDTH // 2, 200)
        
        # 游戏说明
        instructions = [
            "点击箭头，让它飞出棋盘",
            "前方无阻挡即可消除",
            "消除所有箭头通关",
        ]
        for i, text in enumerate(instructions):
            draw_text_centered(self.screen, text, self.font_small, DARK_GRAY, 
                              WINDOW_WIDTH // 2, 270 + i * 30)
        
        # 开始按钮
        btn_x = WINDOW_WIDTH // 2 - 100
        btn_y = 350
        hover = btn_x <= self.mouse_pos[0] <= btn_x + 200 and btn_y <= self.mouse_pos[1] <= btn_y + 50
        draw_button(self.screen, "开始游戏", self.font_medium, btn_x, btn_y, 200, 50, BLUE, hover)
        
        # 操作提示
        draw_text_centered(self.screen, "按 R 重新开始 | 按 ESC 返回", self.font_tiny, GRAY, 
                          WINDOW_WIDTH // 2, 550)
    
    def draw_game(self):
        """绘制游戏界面"""
        # 计算棋盘位置
        cell_size = min(60, (WINDOW_WIDTH - 200) // self.game.cols, 
                       (WINDOW_HEIGHT - 150) // self.game.rows)
        self.game.cell_size = cell_size
        board_width = self.game.cols * cell_size
        board_height = self.game.rows * cell_size
        self.game.board_x = (WINDOW_WIDTH - board_width) // 2
        self.game.board_y = 80 + (WINDOW_HEIGHT - 80 - board_height) // 2
        
        # 绘制顶部信息栏
        self.draw_info_bar()
        
        # 绘制棋盘背景
        pygame.draw.rect(self.screen, BOARD_BG, 
                        (self.game.board_x - 5, self.game.board_y - 5, 
                         board_width + 10, board_height + 10), 
                        border_radius=10)
        pygame.draw.rect(self.screen, CELL_BORDER, 
                        (self.game.board_x - 5, self.game.board_y - 5, 
                         board_width + 10, board_height + 10), 
                        2, border_radius=10)
        
        # 绘制网格
        for r in range(self.game.rows):
            for c in range(self.game.cols):
                x = self.game.board_x + c * cell_size
                y = self.game.board_y + r * cell_size
                pygame.draw.rect(self.screen, CELL_BORDER, (x, y, cell_size, cell_size), 1)
        
        # 绘制箭头
        for arrow in self.game.arrows:
            if not arrow.alive:
                continue
            
            x = self.game.board_x + arrow.col * cell_size
            y = self.game.board_y + arrow.row * cell_size
            
            # 碰撞动画效果
            if arrow.collision_anim > 0:
                # 晃动效果
                shake_x = math.sin(arrow.collision_anim * 0.5) * 5
                shake_y = math.cos(arrow.collision_anim * 0.5) * 3
                x += shake_x
                y += shake_y
                color = RED
                alpha = 200 + int(55 * math.sin(arrow.collision_anim * 0.3))
            elif arrow == self.hovered_arrow:
                # 悬停效果
                color = (min(ARROW_COLORS[arrow.direction][0] + 40, 255),
                        min(ARROW_COLORS[arrow.direction][1] + 40, 255),
                        min(ARROW_COLORS[arrow.direction][2] + 40, 255))
                alpha = 255
            else:
                color = ARROW_COLORS[arrow.direction]
                alpha = 255
            
            draw_arrow(self.screen, x, y, cell_size - 8, arrow.direction, color, alpha)
        
        # 绘制提示箭头
        if self.hint_system and self.hint_system.is_hint_active():
            hint_arrow = self.hint_system.get_hint_arrow()
            if hint_arrow and hint_arrow.alive:
                hx = self.game.board_x + hint_arrow.col * cell_size
                hy = self.game.board_y + hint_arrow.row * cell_size
                # 闪烁效果
                flash_alpha = int(200 + 55 * math.sin(self.hint_system.hint_timer * 0.2))
                draw_arrow(self.screen, hx, hy, cell_size - 8, hint_arrow.direction, YELLOW, flash_alpha)
        
        # 绘制飞出的箭头
        for arrow in self.game.flying_arrows:
            progress = arrow.fly_progress
            x = self.game.board_x + arrow.col * cell_size
            y = self.game.board_y + arrow.row * cell_size
            
            # 根据方向计算飞出位置
            if arrow.direction == UP:
                y -= progress * 300
            elif arrow.direction == DOWN:
                y += progress * 300
            elif arrow.direction == LEFT:
                x -= progress * 300
            elif arrow.direction == RIGHT:
                x += progress * 300
            
            alpha = int(255 * (1 - progress))
            draw_arrow(self.screen, x, y, cell_size - 8, arrow.direction, 
                      ARROW_COLORS[arrow.direction], alpha)
        
        # 绘制重新开始按钮
        btn_x = WINDOW_WIDTH - 150
        btn_y = 20
        hover = btn_x <= self.mouse_pos[0] <= btn_x + 120 and btn_y <= self.mouse_pos[1] <= btn_y + 40
        draw_button(self.screen, "重新开始", self.font_small, btn_x, btn_y, 120, 40, DARK_GRAY, hover)
        
        # 绘制提示按钮
        btn_x2 = WINDOW_WIDTH - 150
        btn_y2 = 70
        hover2 = btn_x2 <= self.mouse_pos[0] <= btn_x2 + 120 and btn_y2 <= self.mouse_pos[1] <= btn_y2 + 40
        draw_button(self.screen, "提示", self.font_small, btn_x2, btn_y2, 120, 40, GREEN, hover2)
        
        # 绘制静音按钮
        btn_x3 = WINDOW_WIDTH - 150
        btn_y3 = 120
        hover3 = btn_x3 <= self.mouse_pos[0] <= btn_x3 + 120 and btn_y3 <= self.mouse_pos[1] <= btn_y3 + 40
        mute_text = "静音" if self.sound_manager.enabled else "开启音效"
        draw_button(self.screen, mute_text, self.font_small, btn_x3, btn_y3, 120, 40, DARK_GRAY, hover3)
    
    def draw_info_bar(self):
        """绘制信息栏"""
        # 关卡名称
        draw_text_centered(self.screen, self.game.get_level_name(), self.font_medium, BLACK, 
                          WINDOW_WIDTH // 2, 30)
        
        # 剩余箭头
        remaining = self.game.get_remaining_arrows()
        draw_text_centered(self.screen, f"剩余箭头: {remaining}", self.font_small, DARK_GRAY, 
                          120, 30)
        
        # 失误次数
        errors_left = self.game.max_errors - self.game.errors
        error_color = RED if errors_left <= 1 else DARK_GRAY
        draw_text_centered(self.screen, f"失误次数: {errors_left}", self.font_small, error_color, 
                          120, 55)
    
    def draw_level_complete(self):
        """绘制通关界面"""
        # 背景遮罩
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        self.screen.blit(overlay, (0, 0))
        
        # 通关信息
        draw_text_centered(self.screen, "恭喜通关！", self.font_large, GREEN, 
                          WINDOW_WIDTH // 2, 200)
        draw_text_centered(self.screen, self.game.get_level_name() + " 完成", self.font_medium, WHITE, 
                          WINDOW_WIDTH // 2, 260)
        draw_text_centered(self.screen, f"失误次数: {self.game.errors}", self.font_small, WHITE, 
                          WINDOW_WIDTH // 2, 310)
        
        # 下一关按钮
        btn_x = WINDOW_WIDTH // 2 - 100
        btn_y = 400
        hover = btn_x <= self.mouse_pos[0] <= btn_x + 200 and btn_y <= self.mouse_pos[1] <= btn_y + 50
        
        import levels as lvl
        if self.game.current_level + 1 < len(lvl.LEVELS):
            draw_button(self.screen, "下一关", self.font_medium, btn_x, btn_y, 200, 50, GREEN, hover)
        else:
            draw_button(self.screen, "查看结果", self.font_medium, btn_x, btn_y, 200, 50, GREEN, hover)
    
    def draw_lose(self):
        """绘制失败界面"""
        # 背景遮罩
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        self.screen.blit(overlay, (0, 0))
        
        # 失败信息
        draw_text_centered(self.screen, "游戏失败", self.font_large, RED, 
                          WINDOW_WIDTH // 2, 200)
        draw_text_centered(self.screen, "失误次数已用尽", self.font_medium, WHITE, 
                          WINDOW_WIDTH // 2, 260)
        draw_text_centered(self.screen, self.game.get_level_name(), self.font_small, WHITE, 
                          WINDOW_WIDTH // 2, 310)
        
        # 重新开始按钮
        btn_x = WINDOW_WIDTH // 2 - 100
        btn_y = 400
        hover = btn_x <= self.mouse_pos[0] <= btn_x + 200 and btn_y <= self.mouse_pos[1] <= btn_y + 50
        draw_button(self.screen, "重新开始", self.font_medium, btn_x, btn_y, 200, 50, BLUE, hover)
    
    def draw_win(self):
        """绘制游戏通关界面"""
        # 背景遮罩
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        self.screen.blit(overlay, (0, 0))
        
        # 通关信息
        draw_text_centered(self.screen, "恭喜通关！", self.font_large, YELLOW, 
                          WINDOW_WIDTH // 2, 180)
        draw_text_centered(self.screen, "你已完成所有关卡！", self.font_medium, WHITE, 
                          WINDOW_WIDTH // 2, 240)
        draw_text_centered(self.screen, "感谢游玩", self.font_small, WHITE, 
                          WINDOW_WIDTH // 2, 290)
        
        # 返回主菜单按钮
        btn_x = WINDOW_WIDTH // 2 - 100
        btn_y = 400
        hover = btn_x <= self.mouse_pos[0] <= btn_x + 200 and btn_y <= self.mouse_pos[1] <= btn_y + 50
        draw_button(self.screen, "返回主菜单", self.font_medium, btn_x, btn_y, 200, 50, BLUE, hover)


def main():
    """主函数"""
    app = ArrowGameApp()
    app.run()


if __name__ == "__main__":
    main()
