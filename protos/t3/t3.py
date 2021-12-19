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

class GameBoard:

    def __init__(self, size = 3):
        self.size = 3 # 3 width/height
        self.data = []

        self.reset()

    def reset(self):
        self.data = [0,0,0,0,0,0,0,0,0]

    def get(self, x, y ):
        pos = (x*self.size) + y
        return self.data[pos]

    def get_position(self, position):
        return self.data[position]

    def set(self, x, y, value):
        pos = (x*self.size) + y
        self.data[pos] = value
        return self.data[pos] == value

    def set_position(self, position, value):
        self.data[position] = value

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
    WON = 1
    DEADLOCK = 2

    board: GameBoard

    def __init__(self, board: GameBoard):
        self.board = board
        self.scores = {'human': 0, 'cpu': 0}
        self.status = self.PLAYING

    def attempt_move(self, x, y, player):
        if self.board.get(x, y) == self.EMPTY:
            self.board.set(x, y, player)
            print(f"Set {x=}, {y=} to {player=}")
            return True

        print(f"Failed {x=}, {y=} to {player=}")
        return False

    def cpu_move(self):
        moves = []
        for pos, value in enumerate(self.board.data):
            if value == 0:
                moves.append(pos)

        if len(moves) > 0:
            move = random.choice(moves)
            self.board.set_position(move, self.CPU)


    def has_winner(self):

        possible_winner = self.check()

        if possible_winner == self.HUMAN:
            self.scores['human'] += 1
            return "human"
        elif possible_winner == self.CPU:
            self.scores['cpu'] += 1
            return "cpu"

        return False

    def has_free_move(self):
        return 0 in self.board.data




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
                        collect.append(self.board.get_position(index) == player)

                    if all(collect) is True:
                        return player

        return False

    def toJSON(self):
        return self.board.toJSON()






class GameConnection(QObject):

    def __init__(self, game_logic:GameLogic):
        QObject.__init__(self, None)
        # super(QObject, self).__init__()

        self.logic = game_logic
        self.view = None

        self.page = None
        self.view = None

    def wantPage(self, pageObj):
        self.page = pageObj

    def wantView(self, view):
        self.view = view

    def do_update(self):
        # update scores
        # update state
        self.stateChanged.emit()

    stateChanged = Signal()

    @Slot(result=str)
    def getState(self):
        return self.logic.toJSON()


    @Slot(result=str)
    def getScore(self):
        human = 0
        cpu = 0

        return dumps(dict(human=human, cpu=cpu))


    # TODO - state property doesn't seem to want to update.  Need to do research on why
    state = Property(str, getState)

    @Slot(int, int, result=bool)
    def attempt(self, x, y):

        if self.logic.status != self.logic.PLAYING:
            if self.logic.status == self.logic.DEADLOCK:
                print("No more moves")
            elif self.logic.status== self.logic.WON:
                print("Someone has won!")

            return



        try:
            print(f"Attempting move ({x=}, {y})")
            result = self.logic.attempt_move(x, y, self.logic.HUMAN)
            status = self.logic.has_winner()
            if status is not False:
                self.logic.status = self.logic.WON
                self.logic.scores['human'] += 1
                print("TODO - Announce winner is likely human")
                return

            self.logic.cpu_move()

            status = self.logic.has_winner()
            if status is not False:
                self.logic.status = self.logic.WON
                self.logic.scores['cpu'] += 1
                print("TODO - Announce winner is likely cpu")
                return
        finally:
            self.do_update()

        return

    @Slot(result=bool)
    def reset(self):
        print("Game is being reset")
        self.logic.board.reset()
        self.stateChanged.emit()
        return True

    @Slot(result=bool)
    def clear_score(self):
        return False



def main(argv):

    main_view = (Path(__file__).parent / 'view' / 'main.html')
    assert main_view.exists()

    bridge = GameConnection(GameLogic(GameBoard()))
    GenerateApp("Tic-tac-toe", dict(height=400, width=350), main_view, bridge, main_view.parent, enable_debug=True)


if __name__ == "__main__":
    main(sys.argv)
