import sys
import typing as T
from pathlib import Path

from PySide2 import QtWidgets
from PySide2 import QtCore
from PySide2 import QtGui

from PySide2 import QtWebEngineWidgets
from PySide2.QtWebEngineWidgets import QWebEnginePage
from PySide2.QtWebChannel import QWebChannel


class SeedPage(QWebEnginePage):

    def __init__(self, parent = None, switchboard = None):
        QWebEnginePage.__init__(self, parent)


        if switchboard is None:
            raise ValueError("Switchboard/backend instance must be passed to SeedPage initializer")

        self.switchboard = switchboard
        self.loadFinished.connect(self.onLoadFinished)
        print("SeedPage init'd")



    @QtCore.Slot(bool)
    def onLoadFinished(self, ok):
        if ok:
            self.load_qwebchannel()
            self.load_switchboard()
            print("on loaded")

    def load_qwebchannel(self):
        file = QtCore.QFile(":/qtwebchannel/qwebchannel.js")
        if file.open(QtCore.QIODevice.ReadOnly):
            content = file.readAll()
            file.close()
            self.runJavaScript(content.data().decode())
        if self.webChannel() is None:
            channel = QWebChannel(self)
            self.setWebChannel(channel)

    def load_switchboard(self):

        if hasattr(self.switchboard, 'wantPage'):
            self.switchboard.wantPage(self)

        if self.webChannel() is not None:
            self.webChannel().registerObject('switchboard', self.switchboard)

            script = r"""    
                        new QWebChannel(qt.webChannelTransport, function(channel){
                            console.log(channel);
                            window.switchboard = channel.objects.switchboard;
                            app_loaded(channel);
                        });
            """
            self.runJavaScript(script)


    def javaScriptConsoleMessage(self, level:QtWebEngineWidgets.QWebEnginePage.JavaScriptConsoleMessageLevel, message:str, lineNumber:int, sourceID:str) -> None:
        # QWebEnginePage.javaScriptConsoleMessage(self, level, message, lineNumber, sourceID)
        log_level = {
            QWebEnginePage.JavaScriptConsoleMessageLevel.InfoMessageLevel: "INFO",
            QWebEnginePage.JavaScriptConsoleMessageLevel.ErrorMessageLevel: "ERROR",
            QWebEnginePage.JavaScriptConsoleMessageLevel.WarningMessageLevel: "WARNING"
        }

        if level in log_level:
            level = log_level[level]

        print("console.log:", level, message, lineNumber, sourceID)





class DeskManDebugWidget(QtWidgets.QWidget):

    def __init__(self, *args, **kwargs):
        QtWidgets.QWidget.__init__(self, *args, **kwargs)
        # super(QtWidgets.QWidget, self).__init__(*args, **kwargs)

        self.layout = None
        self.debugger = None
        self.setup_ui()

    def setup_ui(self):
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setContentsMargins(0,0,0,0)

        self.debugger = QtWebEngineWidgets.QWebEngineView(self)
        self.layout.addWidget(self.debugger)
        self.setGeometry(0,0, 800, 400)



    def attach_to_webview(self, browser: QtWebEngineWidgets.QWebEngineView):
        browser.page().setDevToolsPage(self.debugger.page())



class DeskManWidget(QtWidgets.QWidget):


    def setup_ui(self):

        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setContentsMargins(0,0,0,0)
        self.browser = QtWebEngineWidgets.QWebEngineView(self)
        self.browser.setContextMenuPolicy(QtCore.Qt.NoContextMenu)

        #TODO make this user/app configurable and not hardwired
        self.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint);

        self.layout.addWidget(self.browser)

    def center(self):
        # https://python-commandments.org/pyqt-center-window/

        qr = self.frameGeometry()
        cp = QtWidgets.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())


    def closeEvent(self, event:QtGui.QCloseEvent) -> None:
        # Shut down the application if the main widget is closed
        try:
            app = QtWidgets.QApplication.instance()
            app.closeAllWindows()
        except KeyboardInterrupt:
            # try again
            app = QtWidgets.QApplication.instance()
            app.closeAllWindows()


class Generator:

    height: int
    width: int
    seed: T.Union[str, Path]
    switchboard_obj: QtCore.QObject
    view_dir: T.Union[str, Path]
    view: QtWidgets.QWidget
    debugger: T.Union[None, QtWidgets.QWidget]
    app: QtWidgets.QApplication

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

        if isinstance(seed, str):
            if Path(seed).exists() is True and seed.startswith("./"):
                seed = Path(seed).absolute()
            elif Path(seed) is False and seed.startswith("./"):
                seed = (Path.cwd() / seed)

            if Path(seed).exists() is False:
                raise ValueError(f"Unable to find seed/starting view @ {seed=}")

        self.height = dims['height']
        self.width = dims['width']
        self.seed = seed
        self.seed_url = None
        self.seed_page = None
        self.switchboard_obj = switchboard

        self.view_dir = view_dir

        self.view = None
        self.debugger = None

        self.app = None

    def build(self, argv, enable_debug = False):

        self.app = QtWidgets.QApplication(argv)

        self.view = DeskManWidget()
        self.view.setup_ui()
        self.view.setWindowTitle(self.title)

        self.view.setGeometry(0, 0, self.width, self.height)
        self.view.center()

        if hasattr(self.switchboard_obj, 'wantView'):
            self.switchboard_obj.wantView(self.view)

        self.seed_url = QtCore.QUrl.fromLocalFile(str(self.seed))
        self.seed_page = SeedPage(None, self.switchboard_obj)
        self.seed_page.load(self.seed_url)
        self.view.browser.setPage(self.seed_page)

        # debugger
        if enable_debug is True:
            self.debugger = DeskManDebugWidget()
            self.debugger.attach_to_webview(self.view.browser)


    def run(self):
        self.view.show()
        if self.debugger is not None:
            self.debugger.show()

        sys.exit(self.app.exec_())


def GenerateApp(title, dims, seed_page, switchboard, view_dir=None, enable_debug=False):

    desktop = Generator(title, dims, seed_page, switchboard, view_dir)

    desktop.build(sys.argv, enable_debug = enable_debug)
    desktop.view.show()

    desktop.run()


QuickStart = GenerateApp
