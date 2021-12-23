from pathlib import Path

from pydeskman import GenerateApp
from pydeskman import QObject, Slot, Signal, Property

class Switchboard(QObject):

    def __init__(self, music_manager):
        self.manager = music_manager

        QObject.__init__(self)



class MusicManager:
    pass




def main():
    musicman = MusicManager()
    switchboard = Switchboard(musicman)

    HERE = Path(__file__).parent

    app = GenerateApp("Music player", dict(width=600, height=250), HERE / "view/main.html", switchboard, enable_debug=True)


if __name__ == "__main__":
    main()