import sys

from PySide2 import QtWidgets
from PySide2 import QtCore

from PySide2 import QtWebEngineWidgets
from PySide2.QtWebChannel import QWebChannel


class DeskManDebugWidget(QtWidgets.QWidget):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setup_ui()

    def setup_ui(self):
        self.layout = QtWidgets.QVBoxLayout(self)
        self.debugger = QtWebEngineWidgets.QWebEngineView(self)
        self.layout.addWidget(self.debugger)
        self.setGeometry(0,0, 800, 400)




    def attach_to_webview(self, browser: QtWebEngineWidgets.QWebEngineView):
        browser.page().setDevToolsPage(self.debugger.page())



class DeskManWidget(QtWidgets.QWidget):


    def setup_ui(self):

        self.layout = QtWidgets.QVBoxLayout(self)
        self.browser = QtWebEngineWidgets.QWebEngineView(self)
        self.browser.setContextMenuPolicy(QtCore.Qt.NoContextMenu)

        self.layout.addWidget(self.browser)

    def center(self):
        # https://python-commandments.org/pyqt-center-window/

        qr = self.frameGeometry()
        cp = QtWidgets.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())


class Generator:

    def __init__(self, title, dims, seed, switchboard, view_dir = None):
        """

        :param title: string title
        :param dims: dict with integer keys height and width
        :param seed: a relative/absolute file link to the starting html view.
        :param switchboard: a QTObject inheriting class def
        :param view_dir: an absolute directory that contains web view accessible assets.
        """
        self.title = title
        if 'height' not in dims:
            raise ValueError("dims param must be a dict with a `height` key.")

        if 'width' not in dims:
            raise ValueError("dims param must be a dict with a `width` key")

        self.height = dims['height']
        self.width = dims['width']
        self.seed = seed
        self.seed_url = None
        self.seed_page = None
        self.switchboard = switchboard
        self.switchboard_obj = None
        self.switchchannel = None
        self.view_dir = view_dir

        self.view = None
        self.debugger = None

    def build(self, app, enable_debug = False):

        self.view = DeskManWidget()
        self.view.setup_ui()
        self.view.setWindowTitle(self.title)

        self.view.setGeometry(0, 0, self.width, self.height)
        self.view.center()

        self.seed_url = QtCore.QUrl.fromLocalFile(str(self.seed))
        self.seed_page = QtWebEngineWidgets.QWebEnginePage()
        self.seed_page.setUrl(self.seed_url)

        self.attach_switchboard()

        self.view.browser.setPage(self.seed_page)


        # debugger
        if enable_debug is True:
            self.debugger = DeskManDebugWidget()
            self.debugger.attach_to_webview(self.view.browser)
            self.debugger.show()




    def attach_switchboard(self):

        self.switchboard_obj = self.switchboard()
        self.switchchannel = QWebChannel(self.view)
        self.switchchannel.registerObject('switchboard', self.switchboard_obj)
        self.seed_page.setWebChannel(self.switchchannel)







def GenerateApp(title, dims, seed_page, switchboard, view_dir=None, enable_debug=True):

    desktop = Generator(title, dims, seed_page, switchboard, view_dir)

    app = QtWidgets.QApplication(sys.argv)
    desktop.build(app, enable_debug = enable_debug)
    desktop.view.show()

    sys.exit(app.exec_())
