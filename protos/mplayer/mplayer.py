from pathlib import Path

from pydeskman import GenerateApp
from pydeskman import QObject, Slot, Signal, Property

from pybass3 import Song






class MusicManager:

    _current_song: Song

    def __init__(self):
        self._current_song = None

    def load_song(self, song_path):
        self._current_song = Song(song_path)

    def play(self):
        assert self._current_song is not None
        self._current_song.play()

    def stop(self):
        assert self._current_song is not None
        self._current_song.stop()

    def pause(self):
        assert self._current_song is not None
        self._current_song.pause()


class Switchboard(QObject):

    manager: MusicManager

    def __init__(self, music_manager):
        self.manager = music_manager

        QObject.__init__(self)

    @Slot(result=bool)
    def request_load_dlg(self):
        pass

    @Slot(result=bool)
    def play(self):
        self.manager.play()

    @Slot(result=bool)
    def stop(self):
        self.manager.stop()

    @Slot(result=bool)
    def pause(self):
        self.manager.pause()

    @Slot(int, result=bool)
    def seek(self, position):
        """

        :param position: 0 to 100
        :return:
        """
        pass




def main():
    musicman = MusicManager()
    switchboard = Switchboard(musicman)

    HERE = Path(__file__).parent

    app = GenerateApp("Music player", dict(width=600, height=250), HERE / "view/main.html", switchboard, enable_debug=True)


if __name__ == "__main__":
    main()