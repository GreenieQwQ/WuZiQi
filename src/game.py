# 可视化以及棋盘的非算法相关部分参考了https://github.com/junxiaosong/AlphaZero_Gomoku

from __future__ import print_function
import numpy as np


class BasePlayer:
    # 由server赋予index
    def set_player_ind(self, p):
        self.player = p

    def get_action(self, board):
        return board.sensible_moves()[0]

    def statistics(self):
        pass


class Board:
    """board for the game"""

    def __init__(self, **kwargs):
        self.width = int(kwargs.get('width', 11))
        self.height = int(kwargs.get('height', 11))
        # 记录棋盘的状态
        # key: 在棋盘上的位置（以一维数组索引）
        # value: 下棋的player
        self.states = {}
        # need how many pieces in a row to win
        self.n_in_row = int(kwargs.get('n_in_row', 5))
        self.players = [0, 1]  # player1 and player2

    # 初始化
    def init_board(self, start_player=0):
        if self.width < self.n_in_row or self.height < self.n_in_row:
            raise Exception('board width and height can not be '
                            'less than {}'.format(self.n_in_row))
        self.current_player = self.players[start_player]  # start player
        # keep available moves in a list
        self.availables = list(range(self.width * self.height))
        self.states = {}
        # self.last_move = None

    def move_to_location(self, move):
        """
        3*3 board's looks like:
            0 1 2
          2 6 7 8
          1 3 4 5
          0 0 1 2
        and move 5's location is (1,2)
        """
        h = move // self.width
        w = move % self.width
        return h, w

    def location_to_move(self, location):
        if len(location) != 2:
            return None
        h = location[0]
        w = location[1]
        move = h * self.width + w
        if move not in range(self.width * self.height):
            return None
        return move

    # 判断move是否明智
    def is_sensible_move(self, move):
        # 邻居
        nei = [move - 1, move + 1, move - self.width, move + self.width,
               move - self.width - 1, move - self.width + 1, move + self.width - 1, move + self.width + 1]
        h = move // self.width
        w = move % self.width
        # 邻居是否有已下的子
        for chess in nei:
            if chess in range(self.width * self.height) and chess in self.states:
                hh, ww = self.move_to_location(chess)
                # 因为是一维数组 需要此条件保证不会出现跨边的情形
                if abs(h - hh) + abs(w - ww) <= 2:
                    return True
        # endfor
        return False

    # 获取availables中理智的下子
    def sensible_moves(self):
        if len(self.availables) == self.width * self.height:
            result_set = set([self.width // 2 * self.height + self.width // 2])
        else:
            result_set = set([m for m in self.availables if self.is_sensible_move(m)])

        # 随机排序
        # result = list(result_set)
        # np.random.shuffle(result)
        # return  result

        # 不排序
        # return [self.width // 2 * self.height + self.width // 2] if len(self.availables) == self.width * self.height \
        #         else [m for m in self.availables if self.is_sensible_move(m)]

        # 优先连子排序
        result = []
        cnt3 = self.count_all_x_in_row(3)
        cnt4 = self.count_all_x_in_row(4)
        for m in result:
            self.do_move(m)
            newCnt3 = self.count_all_x_in_row(3)
            newCnt4 = self.count_all_x_in_row(4)
            self.cancel_move(m)
            if np.all((cnt3 - newCnt3) != 0) or np.all((cnt4 - newCnt4) != 0):
                result.append(m)

        remains_set = result_set - set(result)
        remains = [m for m in remains_set]
        result += remains
        return result

    # 悔棋
    def cancel_move(self, m):
        try:
            self.states.pop(m)
            self.availables.append(m)
            # 更换对手
            self.current_player = (
                self.players[0]
                if self.current_player == self.players[1]
                else self.players[1]
            )
        except KeyError:
            print("WARNING: key doesn't exist.")

    # 下棋
    def do_move(self, move):
        self.states[move] = self.current_player
        # 可下子减少
        self.availables.remove(move)
        # 更换对手
        self.current_player = (
            self.players[0]
            if self.current_player == self.players[1]
            else self.players[1]
        )
        # 记录上一次的行动
        # self.last_move = move

    # 数对于move有多少个player的x连子（仅数右下、左下方向）
    # 连子有三种情形：一种是被挡住一边的 一种是两边都被挡住的 一种是正常的
    def count_x_in_row(self, m, x):
        width = self.width
        height = self.height
        states = self.states
        cnt = np.array([0, 0, 0])
        player = states[m]
        n = x
        h = m // width
        w = m % width

        # 若上一个子为己方的子则不需计算
        # 水平
        if states.get(m - 1, None) != player:
            if (w in range(width - n + 1) and
                    len(set(states.get(i, None) for i in range(m, m + n))) == 1):
                if n != self.n_in_row:  # 5个子不需计算顶格
                    cnt_block = 0
                    if w - 1 < 0 or states.get(m - 1, None) is not None:  # 越界或有子——block
                        cnt_block += 1
                    if w + n >= width or states.get(m + n, None) is not None:
                        cnt_block += 1
                    cnt[cnt_block] += 1
                else:  # 胜利
                    cnt[0] += 1
        # endif

        # 竖直
        if states.get(m - width, None) != player:
            if (h in range(height - n + 1) and
                    len(set(states.get(i, None) for i in range(m, m + n * width, width))) == 1):
                if n != self.n_in_row:  # 5个子不需计算顶格
                    cnt_block = 0
                    if h - 1 < 0 or states.get(m - width, None) is not None:  # 越界或有子——block
                        cnt_block += 1
                    if h + n >= height or states.get(m + n * width, None) is not None:
                        cnt_block += 1
                    cnt[cnt_block] += 1
                else:  # 胜利
                    cnt[0] += 1
        # endif

        # 右下
        if states.get(m - (width + 1), None) != player:
            if (w in range(width - n + 1) and h in range(height - n + 1) and
                    len(set(states.get(i, None) for i in range(m, m + n * (width + 1), width + 1))) == 1):
                if n != self.n_in_row:  # 5个子不需计算顶格
                    cnt_block = 0
                    if (w - 1 < 0 or h - 1 < 0) or states.get(m - (width + 1), None) is not None:  # 越界或有子——block
                        cnt_block += 1
                    if (w + n >= width or h + n >= height) or states.get(m + n * (width + 1), None) is not None:
                        cnt_block += 1
                    cnt[cnt_block] += 1
                else:  # 胜利
                    cnt[0] += 1
        # endif

        # 左下
        if states.get(m - (width - 1), None) != player:
            if (w in range(n - 1, width) and h in range(height - n + 1) and
                    len(set(states.get(i, None) for i in range(m, m + n * (width - 1), width - 1))) == 1):
                cnt_block = 0
                if n != self.n_in_row:  # 5个子不需计算顶格
                    if (w + 1 >= width or h - 1 < 0) or states.get(m - (width - 1), None) is not None:  # 越界或有子——block
                        cnt_block += 1
                    if (w - n < 0 or h + n >= height) or states.get(m + n * (width - 1), None) is not None:
                        cnt_block += 1
                    cnt[cnt_block] += 1
                else:  # 胜利
                    cnt[0] += 1
        # endif

        # if sum(cnt) > 0:
        #     print(cnt, player)
        return cnt, player

    # 计算棋盘中两个player所有连成x的子的个数
    def count_all_x_in_row(self, x):
        width = self.width
        height = self.height
        moved = list(set(range(width * height)) - set(self.availables))
        cntP = np.array([[0, 0, 0], [0, 0, 0]])
        for m in moved:
            cnt, player = self.count_x_in_row(m, x)
            cntP[player] += cnt
        return cntP

    # 评估局势
    # 注意：下一个到谁走有很大关系
    # TODO: 未考虑xx-x的情形
    # TODO: 未消除重复计算3与4的情形
    # TODO: 未计算被挡住了的3、4情形
    def eval_state(self):
        width = self.width
        height = self.height
        curPlayer = self.current_player

        bonus = [1, -1]
        # 到谁下和评估有很大关系
        if curPlayer == self.players[0]:
            bonus[0] *= 1.5
        else:
            bonus[1] *= 1.5
        # endif
        value = 0

        for x in np.arange(5, 2, -1):
            # 计算形成x个子的个数
            cntP = self.count_all_x_in_row(x)
            for player, cnt in enumerate(cntP):
                for i, c in enumerate(cnt):
                    # 为了打破僵局 加分加上bonus
                    value += c * (10 ** (x - i)) * bonus[player]  # max player = 1 min = -1
            # last_cnt = cnt

        moved = list(set(range(width * height)) - set(self.availables))
        for m in moved:
            h, w = self.move_to_location(m)
            value += (1 if (abs(h - height / 2) <= height / 4 and abs(w - width / 2) <= width / 4) else 0) * bonus[
                player]
        #     # last_cnt = np.array([0, 0, 0])
        #     # 从3子开始评估
        #     for x in np.arange(5, 2, -1):
        #         # 计算形成x个子的个数
        #         cnt, player = self.count_x_in_row(m, x)
        #         # realCnt = cnt - last_cnt    # 有多少个n 就会重复计算多少个n-1 需要减去
        #         for i, c in enumerate(cnt):
        #             # 为了打破僵局 加分加上bonus
        #             value += c * (10 ** (x-i)) * bonus[player]   # max player = 1 min = -1
        #         # last_cnt = cnt
        return value

    # 判断是否5子
    def has_a_winner(self):
        width = self.width
        height = self.height
        n = self.n_in_row

        moved = list(set(range(width * height)) - set(self.availables))
        if len(moved) < self.n_in_row * 2 - 1:
            return False, None

        for m in moved:
            cnt, player = self.count_x_in_row(m, n)
            if sum(cnt) >= 1:
                return True, player

        return False, None

    # 有两种游戏结束的方式：一方获胜/没有子下
    def game_end(self):
        win, winner = self.has_a_winner()
        if win:
            return True, winner
        elif len(self.availables) == 0:  # no chess to display
            return True, None
        return False, None

    def get_current_player(self):
        return self.current_player


# 可视化
class Game:
    def __init__(self, board, **kwargs):
        self.board = board

    # 将棋盘打印
    def graphic(self, board, player1, player2):
        width = board.width
        height = board.height

        print("Player", player1, "with X".rjust(3))
        print("Player", player2, "with O".rjust(3))
        print()
        for x in range(width):
            print("{0:8}".format(x), end='')
        print('\r\n')
        for i in range(height - 1, -1, -1):
            print("{0:4d}".format(i), end='')
            for j in range(width):
                loc = i * width + j
                p = board.states.get(loc, None)
                if p == player1:
                    print('X'.center(8), end='')
                elif p == player2:
                    print('O'.center(8), end='')
                else:
                    print('_'.center(8), end='')
            print('\r\n\r\n')
        print("Eval: %d" % board.eval_state())

    # 开始游戏
    def start_play(self, player1: BasePlayer, player2: BasePlayer, start_player=0, count=11 * 11, shown=True):
        self.p1, self.p2 = player1, player2
        if start_player not in (0, 1):
            raise Exception('start_player should be either 0 (player1 first) '
                            'or 1 (player2 first)')
        self.board.init_board(start_player)
        p1, p2 = self.board.players
        player1.set_player_ind(p1)
        player2.set_player_ind(p2)
        players = {p1: player1, p2: player2}
        if shown:
            self.graphic(self.board, player1.player, player2.player)

        i = 0
        while True:
            i += 1
            if i >= count:
                self.statistics()
                if shown:
                    print("Game end for maximum counts.")
                return None
            current_player = self.board.get_current_player()
            player_in_turn = players[current_player]
            move = player_in_turn.get_action(self.board)
            self.board.do_move(move)
            if shown:
                self.graphic(self.board, player1.player, player2.player)
            end, winner = self.board.game_end()
            if end:
                self.statistics()
                if shown:
                    if winner is not None:
                        print("Game end. Winner is", players[winner])
                    else:
                        print("Game end. Tie")
                return winner

    # 打印记录
    def statistics(self):
        self.p1.statistics()
        self.p2.statistics()
