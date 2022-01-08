import sys

from pydeskman import QuickStart, QObject

class FormBridge(QObject):
    pass

def main(argv):

    bridge = FormBridge()
    app = QuickStart("Forms", dict(height=450, width=600), "./view/main.html", bridge, enable_debug=True )


if __name__ == "__main__":
    main(sys.argv)