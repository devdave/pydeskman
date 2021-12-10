import sys
from pathlib import Path

from pydeskman import GenerateApp
from pydeskman import QObject

class GameConnection(QObject):

    def wantsApplication(self, app):
        self.app = app





def main(argv):

    main_view = (Path(__file__).parent / 'view' / 'main.html')
    assert main_view.exists()

    GenerateApp("Tic-tac-toe", dict(height=400, width=350), main_view, GameConnection(), main_view.parent, enable_debug=True)


if __name__ == "__main__":
    main(sys.argv)
