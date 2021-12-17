"""
    Tic-Tac-Toe
    ===========

    Somewhat of a disorganized mess.

    
"""

import sys
from pathlib import Path
from json import dumps, loads
from collections import defaultdict
import random

from pydeskman import GenerateApp
from pydeskman import QObject
from pydeskman import Property, Slot, Signal

def coord2int(x, y, size=3):
    return (x*size) + y

def int2coord(index, size=3):
    x = index // size
    y = index - x*size

    return dict(x=x, y=y)

class GameState:

    def __init__(self, size = 3):
        self.size = 3 # 3 width/height
        self.board = []

        self.reset()

    def reset(self):
        self.board = [0,0,0,0,0,0,0,0,0]

    def get(self, x, y ):
        pos = (x*self.size) + y
        return self.board[pos]

    def raw_get(self, position):
        return self.board[position]

    def set(self, x, y, value):
        pos = (x*self.size) + y
        self.board[pos] = value
        return self.board[pos] == value

    def set_position(self, position, value):
        self.board[position] = value

    def toJSON(self):
        result = defaultdict(dict)
        for x in range(0, self.size):
            for y in range(0, self.size):
                result[x][y] = self.get(x, y)

        return dumps(result)


class GameLogic:
    EMPTY = 0
    CPU = 1
    HUMAN = 2

    PLAYING = 0
    WINNER = 1
    DEADLOCK = 2

    state: GameState

    def __init__(self, state: GameState):
        self.state = state
        self.scores = {'human': 0, 'cpu': 0}
        self.status = self.PLAYING

    def attempt_move(self, x, y, player):
        if self.state.get(x, y) == self.EMPTY:
            self.state.set(x, y, player)
            return True

        return False

    def cpu_move(self):
        moves = []
        for pos, value in enumerate(self.state.board):
            if value == 0:
                moves.append(pos)

        if len(moves) > 0:
            move = random.choice(moves)
            self.state.set_position(move, self.CPU)


    def has_winner(self):

        possible_winner = self.check()

        if possible_winner == self.HUMAN:
            self.scores['human'] += 1
            return "human"
        elif possible_winner == self.CPU:
            self.scores['cpu'] += 1
            return "cpu"

        return False



    def check(self):
        # These could be done with vectors BUT hardcode for simplicity
        horz = [
            [coord2int(0, 0), coord2int(0, 1), coord2int(0, 2)],
            [coord2int(1, 0), coord2int(1, 1), coord2int(1, 2)],
            [coord2int(2, 0), coord2int(2, 1), coord2int(2, 2)]
        ]

        vert = [
            [coord2int(0, 0), coord2int(1, 0), coord2int(2, 0)],
            [coord2int(0, 1), coord2int(1, 1), coord2int(2, 1)],
            [coord2int(0, 2), coord2int(1, 2), coord2int(2, 2)]
        ]

        diag = [
            [coord2int(0, 0), coord2int(1, 1), coord2int(2,2)],
            [coord2int(0, 2), coord2int(1, 1), coord2int(2, 0)]
        ]

        for player in [self.CPU, self.HUMAN]:
            for tests in [horz, vert, diag]:
                for cells in tests:
                    collect = []
                    for index in cells:
                        collect.append(self.state.raw_get(index) == player)

                    if all(collect) is True:
                        return player

        return False

    def toJSON(self):
        return self.state.toJSON()






class GameConnection(QObject):

    def __init__(self, game_logic:GameLogic):
        QObject.__init__(self, None)
        # super(QObject, self).__init__()

        self.logic = game_logic
        self.view = None

    def do_update(self):
        # update scores
        # update state
        self.stateChanged.emit()

    stateChanged = Signal()

    @Slot(result=str)
    def getState(self):
        return self.logic.toJSON()

    state = Property(str, getState)

    @Slot(int, int, result=bool)
    def attempt(self, x, y):
        print(f"Attempting move ({x=}, {y})")
        result = self.logic.attempt_move(x, y, self.logic.HUMAN)
        if result is True:
            print("\tMove accepted")
            self.do_update()
        else:
            print("\t Move Failed")


        return result

    @Slot(result=bool)
    def reset(self):
        print("Game is being reset")
        self.logic.state.reset()
        self.stateChanged.emit()
        return True






def main(argv):

    main_view = (Path(__file__).parent / 'view' / 'main.html')
    assert main_view.exists()

    bridge = GameConnection(GameLogic(GameState()))
    GenerateApp("Tic-tac-toe", dict(height=400, width=350), main_view, bridge, main_view.parent, enable_debug=True)


if __name__ == "__main__":
    main(sys.argv)
