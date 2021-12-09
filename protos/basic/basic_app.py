import pathlib as pl
import sys

from PySide2.QtCore import QObject
from PySide2.QtCore import Slot, Signal

from pydeskman import GenerateApp

home_view = (pl.Path(__file__).parent / "home.html")

class AppLogic(QObject):



    @Slot(str, result=str)
    def hello(self, name):
        print("Greeting client/frontend")
        return f"greetings {name}"

    @Slot(str, result=str)
    def do_cb(self, msg):
        print("I got a message from the frontend", msg)
        self.stuff_happened.emit(msg)
        return f"returning {msg}"

    stuff_happened = Signal(str)




def main():

    assert home_view.exists(), home_view

    GenerateApp("Test", dict(height=600, width=1200), home_view, AppLogic)



if __name__ == "__main__":
    main()