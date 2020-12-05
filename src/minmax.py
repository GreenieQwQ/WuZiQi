from copy import deepcopy
import numpy as np

INF = 18340206   # 一个十分大的数

class zobrist:
    def __init__(self, w, h):
        self.list = np.random.randint(-INF, INF, size=(w*h, ))  # 随机数组
        self.explored = set()

    def __contains__(self, node):
        return self.hash(node.board) in self.explored

    def append(self, node):
        self.explored.add(self.hash(node.board))

    def hash(self, board):
        h = 0
        for k in board.states:
            h ^= self.list[k]
        return h

class minMax:
    def __init__(self, mode, depth):
        self.player = None
        self.mode = mode
        self.depth = depth

    # 由server赋予index
    def set_player_ind(self, p):
        self.player = p

    def get_action(self, board):
        move = alpha_beta_search(board, mode=self.mode, depth=self.depth)
        if move is None:
            print("WARNING: something might be wrong. Move is None.")
        return move

    def __str__(self):
        return "robert {}".format(self.player)


class TreeNode:
    def __init__(self, board):
        self.board = deepcopy(board)

    def getAction(self):
        # 第一次改进：随机shuffle
        result = self.board.sensible_moves()
        np.random.shuffle(result)
        return result

    def utility(self):
        return self.board.eval_state()

    def terminate(self):
        return self.board.game_end()[0]

    def result(self, act):
        newBoard = deepcopy(self.board)
        newBoard.do_move(act)
        return TreeNode(newBoard)

def min_value(node: TreeNode, alpha, beta, depth, z_list: zobrist):
    if depth == 0 or node.terminate():
        return None, node.utility()

    m = None
    v = INF
    acts = node.getAction()
    for a in acts:
        result = node.result(a)
        if result in z_list:    # 环检测 已探索
            continue
        else:
            z_list.append(result)
        next_act, node_val = max_value(result, alpha, beta, depth-1, z_list)
        if node_val < v:
            m = a
            v = node_val
        if v <= alpha:
            return m, v
        beta = min(beta, v)
    return m, v


def max_value(node: TreeNode, alpha, beta, depth, z_list: zobrist):
    if depth == 0 or node.terminate():
        return None, node.utility()

    m = None
    v = -INF
    acts = node.getAction()
    for a in acts:
        result = node.result(a)
        if result in z_list:  # 环检测 已探索
            continue
        else:
            z_list.append(result)
        next_act, node_val = min_value(result, alpha, beta, depth-1, z_list)
        if node_val > v:
            m = a
            v = node_val
        if v >= beta:
            return m, v
        alpha = max(alpha, v)
    return m, v


def alpha_beta_search(board, depth, mode="max"):
    init_node = TreeNode(board)
    z = zobrist(board.width, board.height)
    if mode == "max":
        m, v = max_value(init_node, -INF, INF, depth, z)
    else:
        m, v = min_value(init_node, -INF, INF, depth, z)
    print(m, v)
    return m



