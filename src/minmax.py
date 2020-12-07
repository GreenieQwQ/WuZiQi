from copy import deepcopy
from game import BasePlayer
import numpy as np
INF = 183402060   # 一个十分大的数

class zobrist:
    def __init__(self, w=11, h=11):
        self.listA = np.random.randint(-((2**31)-1), 2**31, size=(w*h, ))  # 随机数组
        self.listB = np.random.randint(-((2 ** 31) - 1), 2 ** 31, size=(w * h,))  # 随机数组
        self.explored = {}
        self.explored_nodes = 0

    def __contains__(self, node):
        return self.hash(node.board) in self.explored

    def __getitem__(self, node):
        return self.explored[self.hash(node.board)]

    def add(self, node, val, depth):
        self.explored[self.hash(node.board)] = {}
        self.explored[self.hash(node.board)]["val"] = val
        self.explored[self.hash(node.board)]["depth"] = depth

    def hash(self, board):
        h = 0
        for k in board.states:
            h ^= (self.listA[k] if k == board.players[0] else self.listB[k])
        return h

    def clear(self):
        self.explored.clear()

    def updateDepth(self, d=2):
        for k in self.explored:
            self.explored[k]["depth"] += d

class minMax(BasePlayer):
    def __init__(self, mode, depth):
        self.player = None
        self.mode = mode
        self.depth = depth
        self.z = zobrist(11, 11)

    def get_action(self, board):
        self.z.clear()
        move = alpha_beta_search(board, mode=self.mode, depth=self.depth, z=self.z)
        if move is None:
            print("WARNING: something might be wrong. Move is None.")
        return move

    def __str__(self):
        return "robert {}".format(self.player)

    def statistics(self):
        print("robert %d has explored %d nodes." % (self.player, self.z.explored_nodes))


class TreeNode:
    def __init__(self, board):
        self.board = deepcopy(board)

    def count_Blocked_4_changed(self, m):
        origin_cnt4 = self.board.count_all_x_in_row(4)
        self.board.do_move(m)
        after_cnt4 = self.board.count_all_x_in_row(4)
        self.board.cancel_move(m)
        return np.all(origin_cnt4 != after_cnt4)

    def getAction(self):
        result = self.board.sensible_moves()
        return result

    def utility(self):
        return self.board.eval_state()

    def terminate(self):
        return self.board.game_end()[0]

    def result(self, act):
        # newBoard = deepcopy(self.board)
        # newBoard.do_move(act)
        # return TreeNode(newBoard)
        self.board.do_move(act)
        # return self

    def resume(self, act):
        self.board.cancel_move(act)
        # return self


def min_value(node: TreeNode, alpha, beta, depth, z_list: zobrist):
    z_list.explored_nodes += 1
    if depth == 0 or node.terminate():
        return None, node.utility()

    m = None
    v = INF
    acts = node.getAction()
    for a in acts:
        # 冲四延伸
        if node.count_Blocked_4_changed(a):
            elastic = True
        else:
            elastic = False

        # 下一步棋
        if elastic:
            depth += 2
        node.result(a)
        if node in z_list and z_list[node]["depth"] < depth:  # 置换表含有已探索的更深的此节点 注：不能相等 TODO: why
            node_val = z_list[node]["val"]
        else:
            next_act, node_val = max_value(node, alpha, beta, depth-1, z_list)
            z_list.add(node, node_val, depth)
        # 恢复
        node.resume(a)
        if elastic:
            depth -= 2

        if node_val < v:
            m = a
            v = node_val
        if v <= alpha:
            return m, v
        beta = min(beta, v)
    return m, v


def max_value(node: TreeNode, alpha, beta, depth, z_list: zobrist):
    z_list.explored_nodes += 1
    if depth == 0 or node.terminate():
        return None, node.utility()

    m = None
    v = -INF
    acts = node.getAction()
    for a in acts:
        # 冲四延伸
        if node.count_Blocked_4_changed(a):
            elastic = True
        else:
            elastic = False

        # 下一步棋
        if elastic:
            depth += 2

        node.result(a)
        if node in z_list and z_list[node]["depth"] < depth:  # 置换表含有已探索的更深的节点
            node_val = z_list[node]["val"]
        else:
            next_act, node_val = min_value(node, alpha, beta, depth-1, z_list)
            z_list.add(node, node_val, depth)
        # 恢复
        node.resume(a)
        if elastic:
            depth -= 2

        if node_val > v:
            m = a
            v = node_val
        if v >= beta:
            return m, v
        alpha = max(alpha, v)
    return m, v


def alpha_beta_search(board, depth, z, mode):
    init_node = TreeNode(board)
    if mode == "max":
        m, v = max_value(init_node, -INF, INF, depth, z)
    else:
        m, v = min_value(init_node, -INF, INF, depth, z)
    print(m, v)
    return m



