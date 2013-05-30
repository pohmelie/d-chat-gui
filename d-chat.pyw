import sys
import gui
import bnet
import platform
import PySide
from PySide import QtGui


print(platform.python_version())
print(PySide.__version__)
print(PySide.QtCore.__version__)
print(platform.system())

class Dchat():
    def __init__(self, host, port):
        self.account = None
        self.password = None
        self.channel = ""

        self.bnet = bnet.Bnet(host, port, self.login_error, self.chat_event)
        self.gui = gui.Gui()

        self.main_tab = gui.Tab()
        self.gui.addTab(self.main_tab, "main")

        self.main_tab.input.returnPressed.connect(self.on_input)

        self.gui.show()

    def on_input(self):
        txt = self.main_tab.input.text()
        self.main_tab.chat_text.append("<b>" + txt + "</b>")
        self.main_tab.input.clear()

    def login_error(self, packet_id, retcode=None):
        pass

    def chat_event(self, packet):
        pass

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    dchat = Dchat("rubattle.net", 6112)
    sys.exit(app.exec_())
