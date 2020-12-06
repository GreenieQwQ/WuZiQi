from __future__ import print_function
from game import *
from minmax import *

class Human(BasePlayer):
    def __init__(self):
        self.player = None

    def get_action(self, board):
        try:
            location = input("Your move: ")
            if isinstance(location, str):
                location = [int(n) for n in location.split(",")]
            move = board.location_to_move(location)
        except Exception:
            move = None
        if move is None or move not in board.availables:
            print("invalid move")
            move = self.get_action(board)
        return move

    def __str__(self):
        return "Human {}".format(self.player)


def run():
    n = 5
    width, height = 11, 11
    try:
        board = Board(width=width, height=height, n_in_row=n)
        game = Game(board)
        # human player, input your move in the format: 2,3
        # playerMax = Human()
        playerMax = minMax("max", depth=2)
        playerMin = minMax("min", depth=4)

        # set start_player=0 for human first
        game.start_play(playerMax, playerMin, start_player=0, shown=1)
    except KeyboardInterrupt:
        game.statistics()
        print('\nThank you for playing.')


if __name__ == '__main__':
    run()
