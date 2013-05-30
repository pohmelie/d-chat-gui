from PySide import QtCore, QtGui


class ChatText(QtGui.QTextEdit):
    def __init__(self, *args, **kwargs):
        QtGui.QTextEdit.__init__(self, *args, **kwargs)
        self.setFrameShape(QtGui.QFrame.NoFrame)
        self.setReadOnly(True)
        self.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByMouse | QtCore.Qt.TextSelectableByMouse)


class Tab(QtGui.QFrame):
    def __init__(self, prefix="", *args, **kwargs):
        QtGui.QFrame.__init__(self, *args, **kwargs)

        self.chat_text = ChatText()
        self.input = QtGui.QLineEdit()

        gl = QtGui.QGridLayout(self)
        gl.addWidget(self.chat_text, 0, 0)
        gl.addWidget(self.input, 1, 0)


class Gui(QtGui.QTabWidget):
    def __init__(self, *args, **kwargs):
        QtGui.QTabWidget.__init__(self, *args, **kwargs)
        self.setMovable(True)
