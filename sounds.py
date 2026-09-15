# -*- coding: utf-8 -*-
"""
音效生成模块
使用 Pygame 生成简单的游戏音效
"""

import pygame
import numpy as np


def generate_sound(frequency, duration, volume=0.5, sample_rate=44100):
    """生成简单音效"""
    try:
        import numpy as np
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        tone = np.sin(frequency * t * 2 * np.pi) * volume
        # 转换为16位整数
        audio = (tone * 32767).astype(np.int16)
        # 创建立体声
        stereo_audio = np.column_stack((audio, audio))
        sound = pygame.sndarray.make_sound(stereo_audio)
        return sound
    except ImportError:
        # 如果没有numpy，返回None
        return None


class SoundManager:
    """音效管理器"""
    def __init__(self):
        self.enabled = True
        self.sounds = {}
        self.init_sounds()
    
    def init_sounds(self):
        """初始化音效"""
        try:
            pygame.mixer.init()
            
            # 箭头飞出音效
            self.sounds['fly'] = generate_sound(800, 0.2, 0.3)
            
            # 碰撞音效
            self.sounds['collision'] = generate_sound(200, 0.3, 0.4)
            
            # 通关音效
            self.sounds['win'] = generate_sound(600, 0.5, 0.5)
            
            # 失败音效
            self.sounds['lose'] = generate_sound(300, 0.5, 0.4)
            
            # 点击音效
            self.sounds['click'] = generate_sound(1000, 0.1, 0.2)
            
        except Exception as e:
            print(f"音效初始化失败: {e}")
            self.enabled = False
    
    def play(self, sound_name):
        """播放音效"""
        if not self.enabled:
            return
        
        sound = self.sounds.get(sound_name)
        if sound:
            try:
                sound.play()
            except Exception:
                pass
    
    def toggle(self):
        """切换音效开关"""
        self.enabled = not self.enabled
        return self.enabled


# 全局音效管理器实例
sound_manager = None


def get_sound_manager():
    """获取音效管理器单例"""
    global sound_manager
    if sound_manager is None:
        sound_manager = SoundManager()
    return sound_manager
