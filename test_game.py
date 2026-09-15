# -*- coding: utf-8 -*-
"""
游戏测试用例
"""

import sys
sys.path.insert(0, '.')

from game import Game, GameState
from levels import EMPTY, UP, DOWN, LEFT, RIGHT


def test_path_checking():
    """测试路径检测"""
    print("测试路径检测...")
    
    game = Game()
    
    # 测试1: 箭头前方无阻挡
    print("  测试1: 箭头前方无阻挡")
    game.grid = [
        [0, 0, RIGHT],
        [0, 0, 0],
    ]
    game.rows = 2
    game.cols = 3
    game.arrows = []
    
    # 创建箭头
    from game import Arrow
    arrow = Arrow(0, 2, RIGHT)
    game.arrows.append(arrow)
    
    can_fly, blocking = game.check_path(arrow)
    assert can_fly == True, "应该可以飞出"
    assert len(blocking) == 0, "不应该有阻挡"
    print("    [OK] 通过")
    
    # 测试2: 箭头前方有阻挡
    print("  测试2: 箭头前方有阻挡")
    game.grid = [
        [0, 0, RIGHT, 0, UP],
        [0, 0, 0, 0, 0],
    ]
    game.rows = 2
    game.cols = 5
    
    arrow1 = Arrow(0, 2, RIGHT)
    arrow2 = Arrow(0, 4, UP)
    game.arrows = [arrow1, arrow2]
    
    can_fly, blocking = game.check_path(arrow1)
    assert can_fly == False, "应该被阻挡"
    assert len(blocking) > 0, "应该有阻挡信息"
    print("    [OK] 通过")
    
    # 测试3: 向上箭头在边缘
    print("  测试3: 向上箭头在边缘")
    game.grid = [
        [UP, 0, 0],
        [0, 0, 0],
    ]
    game.rows = 2
    game.cols = 3
    
    arrow = Arrow(0, 0, UP)
    game.arrows = [arrow]
    
    can_fly, blocking = game.check_path(arrow)
    assert can_fly == True, "边缘箭头应该可以飞出"
    print("    [OK] 通过")
    
    # 测试4: 向下箭头有阻挡
    print("  测试4: 向下箭头有阻挡")
    game.grid = [
        [DOWN, 0, 0],
        [0, 0, 0],
        [LEFT, 0, 0],
    ]
    game.rows = 3
    game.cols = 3
    
    arrow1 = Arrow(0, 0, DOWN)
    arrow2 = Arrow(2, 0, LEFT)
    game.arrows = [arrow1, arrow2]
    
    can_fly, blocking = game.check_path(arrow1)
    assert can_fly == False, "应该被阻挡"
    print("    [OK] 通过")
    
    # 测试5: 向左箭头无阻挡
    print("  测试5: 向左箭头无阻挡")
    game.grid = [
        [0, 0, LEFT],
    ]
    game.rows = 1
    game.cols = 3
    
    arrow = Arrow(0, 2, LEFT)
    game.arrows = [arrow]
    
    can_fly, blocking = game.check_path(arrow)
    assert can_fly == True, "应该可以飞出"
    print("    [OK] 通过")
    
    print("路径检测测试全部通过！\n")


def test_click_arrow():
    """测试点击箭头"""
    print("测试点击箭头...")
    
    game = Game()
    
    # 测试1: 点击可消除的箭头
    print("  测试1: 点击可消除的箭头")
    game.load_level(0)  # 加载第一关
    
    # 找到一个可以点击的箭头
    for arrow in game.arrows:
        can_fly, _ = game.check_path(arrow)
        if can_fly:
            result, msg = game.click_arrow(arrow.row, arrow.col)
            assert result == True, f"应该成功消除: {msg}"
            assert not arrow.alive, "箭头应该被标记为死亡"
            print(f"    [OK] 消除了 ({arrow.row}, {arrow.col}) 的箭头")
            break
    
    # 测试2: 点击被阻挡的箭头
    print("  测试2: 点击被阻挡的箭头")
    game.restart_level()
    
    for arrow in game.arrows:
        can_fly, _ = game.check_path(arrow)
        if not can_fly:
            initial_errors = game.errors
            result, msg = game.click_arrow(arrow.row, arrow.col)
            assert result == False, f"应该失败: {msg}"
            assert game.errors == initial_errors + 1, "失误次数应该增加"
            print(f"    [OK] 点击被阻挡的箭头，失误次数增加到 {game.errors}")
            break
    
    print("点击箭头测试全部通过！\n")


def test_game_flow():
    """测试游戏流程"""
    print("测试游戏流程...")
    
    game = Game()
    
    # 测试1: 加载关卡
    print("  测试1: 加载关卡")
    result = game.load_level(0)
    assert result == True, "应该成功加载关卡"
    assert game.state == GameState.PLAYING, "状态应该为PLAYING"
    print("    [OK] 通过")
    
    # 测试2: 重新开始
    print("  测试2: 重新开始")
    game.restart_level()
    assert game.errors == 0, "失误次数应该重置"
    assert game.get_remaining_arrows() > 0, "应该有箭头"
    print("    [OK] 通过")
    
    # 测试3: 进入下一关
    print("  测试3: 进入下一关")
    game.state = GameState.LEVEL_COMPLETE
    result = game.next_level()
    assert result == True, "应该成功进入下一关"
    assert game.current_level == 1, "应该是第2关"
    print("    [OK] 通过")
    
    print("游戏流程测试全部通过！\n")


def test_level_validity():
    """测试关卡有效性"""
    print("测试关卡有效性...")
    
    import levels
    
    for i, level_data in enumerate(levels.LEVELS):
        print(f"  测试关卡 {i+1}: {level_data['name']}")
        
        grid = level_data['grid']
        assert len(grid) > 0, "关卡不能为空"
        assert len(grid[0]) > 0, "关卡宽度不能为0"
        
        # 检查是否有箭头
        arrow_count = 0
        for row in grid:
            for cell in row:
                if cell != EMPTY:
                    arrow_count += 1
        
        assert arrow_count > 0, f"关卡 {i+1} 应该有箭头"
        print(f"    [OK] 关卡有效，包含 {arrow_count} 个箭头")
    
    print("关卡有效性测试全部通过！\n")


def main():
    """运行所有测试"""
    print("=" * 50)
    print("一箭又一箭 - 游戏测试")
    print("=" * 50)
    print()
    
    try:
        test_path_checking()
        test_click_arrow()
        test_game_flow()
        test_level_validity()
        
        print("=" * 50)
        print("所有测试通过！")
        print("=" * 50)
        return 0
    except AssertionError as e:
        print(f"测试失败: {e}")
        return 1
    except Exception as e:
        print(f"测试出错: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
