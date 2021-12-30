from pathlib import Path
from json import dumps, loads

import typing as T

from PySide2.QtWidgets import QFileDialog

from pydeskman import GenerateApp
from pydeskman import QObject, Slot, Signal, Property, QTimer

from pybass3 import Song
from pybass3.bass_tags import BassTags


PulseHookCallable = T.Callable[[int, bool], None] # song position in seconds and True if current song is playing


class MusicManager:

    PULSE_TIMER: int = 500  # 500 ms/ or half a second
    pulser: QTimer
    pulse_hook: PulseHookCallable

    _current_song: Song

    def __init__(self):
        self._current_song = None
        self._current_meta = None
        self.pulser = None

    def setHook(self, hook: PulseHookCallable):
        self.pulse_hook = hook

    def start_pulser(self):
        if self.pulser is None:
            self.pulser = QTimer()

        self.pulser.timeout.connect(self.on_pulse)
        self.pulser.start(self.PULSE_TIMER)

    def stop_pulser(self, clear = False):
        if self.pulser is not None:
            self.pulser.stop()

            if clear is True:
                self.pulse= None

    def on_pulse(self):
        if self._current_song is not None and self._current_song.is_playing is True:
            position = self._current_song.position
            self.pulse_hook(position, self._current_song.is_playing)
        else:
            print("Pulser is None or not playing")
            self.stop_pulser()



    def load_song(self, song_path):
        self._current_song = Song(song_path)
        self._current_meta = BassTags.GetDefaultTags(self._current_song.handle)

        return True

    @property
    def meta(self):
        return self._current_meta

    @property
    def song(self) -> Song:
        return self._current_song

    def play(self):
        assert self._current_song is not None
        self._current_song.play()
        self.start_pulser()

    def stop(self):
        assert self._current_song is not None
        self._current_song.stop()
        self.stop_pulser()

    def pause(self):
        assert self._current_song is not None
        self._current_song.pause()
        self.stop_pulser()


class Switchboard(QObject):

    manager: MusicManager

    def __init__(self, music_manager):
        self.manager = music_manager

        QObject.__init__(self)
        self.view = None

        self.manager.setHook(self.on_song_progress)

    def on_song_progress(self, position, is_playing):
        self.songUpdate.emit(position, is_playing)

    def wantView(self, view):
        self.view = view

    @Slot(result=str)
    def request_load_dlg(self):
        dialog = QFileDialog(self.view)
        dialog.setFileMode(QFileDialog.ExistingFile)
        dialog.setNameFilters(["Music files (*.mp3 *.ogg *.wave)", "Any (*)"])

        cwd = str(Path.cwd())

        dialog.setDirectory(cwd)

        if dialog.exec_():
            paths = dialog.selectedFiles()

            print(f"I got {paths=}")
            self.manager.load_song(paths[0])

            filepath = Path(paths[0])
            response = dict(
                filepath=str(filepath),
                name=filepath.name,
                meta=self.manager.meta,
                length=dict(
                    seconds=self.manager.song.duration,
                    string=self.manager.song.duration_time
                ))

            self.newSong.emit(dumps(response))

            return dumps(response)


        return "ERROR_NOSELECT"

    def new_song_loaded(self):
        pass


    @Slot(result=str)
    def currentSong(self):
        response = dict(status=False)
        if self.manager.song is not None:
            response = dict(
                status=True,
                meta=self.manager.meta,
                length=dict(
                    seconds=self.manager.song.duration,
                    string=self.manager.song.duration_time
                ))

        return dumps(response)

    ##################################################################################################################
    # Signals
    #########

    newSong = Signal(str) # provides a JSON'd dict w/title, artist, length: {seconds, string }
    songUpdate = Signal(int, bool) # song position in seconds and is_playing conditional
    playerStatus = Signal(str)
    position = Signal(int)

    @Slot(result=bool)
    def play(self):
        self.manager.play()
        self.playerStatus.emit("playing")
        return True

    @Slot(result=bool)
    def stop(self):
        self.manager.stop()
        self.playerStatus.emit("stopped")
        return True

    @Slot(result=bool)
    def pause(self):
        self.manager.pause()
        self.playerStatus.emit("paused")
        return True

    @Slot(int, result=bool)
    def seek(self, position):
        """

        :param position: 0 to 100
        :return:
        """
        pass




def main(argv):
    musicman = MusicManager()
    switchboard = Switchboard(musicman)

    HERE = Path(__file__).parent

    generator = Generator("Music player", dict(width=600, height=150), HERE / "view/main.html", switchboard)

    generator.build(argv, enable_debug=True)

    generator.run()


if __name__ == "__main__":
    main(sys.argv)
