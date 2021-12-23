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
from pydeskman import QObject, QWidget, QWebEnginePage
from pydeskman import Property, Slot, Signal

def coord2int(x, y, size=3):
    """
        Converts a pair of coordinates to a scalar/index value

    :param x:
    :param y:
    :param size: the width/height of a perfect square
    :return:
    """
    return (x*size) + y

def int2coord(index, size=3):
    """
        Converts a scalar value back to coordinate pairs

    :param index:
    :param size: the width/height of a perfect square
    :return:
    """

    x = index // size
    y = index - x*size

    return dict(x=x, y=y)

class GameBoard:
    """
        Manager around the game board

        TODO - should the board know about player type values (human and cpu)?

    """


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
    # Game board values
    EMPTY = 0
    CPU = 1
    HUMAN = 2

    # Game status/state
    CONTINUE = 0
    PLAYING = 0 # intentional as a synonym
    PLAYER_WON = 1
    CPU_WON = 2
    DEADLOCK = 3 # no more moves
    BAD_MOVE = 4 # move was invalid

    board: GameBoard
    scores: dict
    status: int # Would be better as an enum but wanted to avoid overengineering

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
            return True

        return False

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

    def reset(self):
        self.board.reset()
        self.status = self.PLAYING

    def run(self, x, y):
        """
        :param x: Player attempted cell's x  coordinate
        :param y: Player attemptd cell's y coorinate
        :return: GameLogic.PLAYER_WON, GameLogic.CPU_WON, GameLogic.CONTINUE, GameLogic.DEADLOCK, GameLogic.BAD_MOVE
        """


        """            
            Attempts to let the Human player select a cell
                If not empty return BAD_MOVE
        """
        if self.status != self.PLAYING:
            return self.status

        if self.attempt_move(x, y, self.HUMAN) is False:
            return self.BAD_MOVE

        """
            Check for win condition
                If true, return CPU or HUMAN won
        """
        win_status = self.has_winner()

        if win_status is not False:
            if win_status == "human":
                self.status = self.PLAYER_WON
                return self.PLAYER_WON
            elif win_status == "cpu":
                self.status = self.CPU_WON
                return self.CPU_WON
            else:
                raise ValueError(f"{win_status=}")


        """
            Check for deadlock
                return DEADLOCK if no more moves possible
        """

        if self.has_free_move() is False:
            self.status = self.DEADLOCK
            return self.DEADLOCK


        """
    
            Attempt to let CPU select a cell

            Check for win condition
                if true return CPU or Human won
        """
        if self.cpu_move() is True:

            win_status = self.has_winner()

            if win_status is not False:
                if win_status == "human":
                    self.status = self.PLAYER_WON
                    return self.PLAYER_WON
                elif win_status == "cpu":
                    self.status = self.CPU_WON
                    return self.CPU_WON
                else:
                    raise ValueError(f"{win_status=}")

        """

        check for deadlock
            return DEADLOCK

        else return CONTINUE
        """
        if self.has_free_move is False:
            self.status = self.DEADLOCK
            return self.DEADLOCK


        return self.PLAYING






class GameConnection(QObject):

    view:QWidget
    page:QWebEnginePage

    def __init__(self, game_logic:GameLogic):
        QObject.__init__(self, None)
        # super(QObject, self).__init__()

        self.logic = game_logic
        self.view = None

        self.page = None
        self.view = None

    def wantPage(self, pageObj: QWebEnginePage):
        self.page = pageObj

    def wantView(self, view: QWidget):
        self.view = view

    def do_update(self):
        # update scores
        # update state
        self.stateChanged.emit()

    stateChanged = Signal()
    hasMessage = Signal(str)

    @Slot(result=str)
    def getState(self):
        return self.logic.toJSON()


    @Slot(result=str)
    def getScore(self):
        return dumps(self.logic.scores)


    # TODO - state property doesn't seem to want to update.  Need to do research on why
    state = Property(str, getState)

    @Slot(int, int, result=bool)
    def attempt(self, x, y):

        # TODO move this to GameLogic

        result = self.logic.run(x, y)

        if result == self.logic.PLAYER_WON:
            print("Player won")
            self.hasMessage.emit("Player won")

        elif result == self.logic.CPU_WON:
            print("CPU won")
            self.hasMessage.emit("CPU won")

        elif result == self.logic.DEADLOCK:
            print("No more moves")
            self.hasMessage.emit("No more moves")

        else:
            print(f"state {result=}")

        self.do_update()
        return True

    @Slot(result=bool)
    def reset(self):
        print("Game is being reset")
        self.logic.reset()

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
