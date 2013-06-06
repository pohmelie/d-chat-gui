from PySide import QtCore, QtGui


class ChatText(QtGui.QTextEdit):
    def __init__(self, *args, **kwargs):
        QtGui.QTextEdit.__init__(self, *args, **kwargs)
        #self.setFrameShape(QtGui.QFrame.NoFrame)
        self.setReadOnly(True)
        self.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByMouse | QtCore.Qt.TextSelectableByMouse)


class Input(QtGui.QTextEdit):

    returnPressed = QtCore.Signal(str)

    def __init__(self, *args, **kwargs):
        QtGui.QTextEdit.__init__(self, *args, **kwargs)
        #self.setFrameShape(QtGui.QFrame.NoFrame)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setWordWrapMode(QtGui.QTextOption.NoWrap)
        self.setTabChangesFocus(True)
        self.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        self.setFixedHeight(self.sizeHint().height())
        self.setAcceptRichText(False)

    def sizeHint(self):
        fm = QtGui.QFontMetrics(self.font())
        return QtCore.QSize(fm.width("x"), fm.height() + 4)

    def keyPressEvent(self, e):
        if e.key() in (QtCore.Qt.Key_Enter, QtCore.Qt.Key_Return):
            e.ignore()
            self.returnPressed.emit(self.toPlainText())
            self.clear()
        else:
            super().keyPressEvent(e)
            tc = self.textCursor()
            tc.select(QtGui.QTextCursor.WordUnderCursor)
            tc = tc.selectedText()
            if " " not in self.toPlainText().strip():
                com.setCompletionPrefix(tc)
                popup = com.popup()
                popup.setCurrentIndex(com.completionModel().index(0,0))
                cr = self.cursorRect()
                cr.setWidth(com.popup().sizeHintForColumn(0)
                    + com.popup().verticalScrollBar().sizeHint().width())
                com.complete(cr)


class Tab(QtGui.QFrame):
    def __init__(self, *args, **kwargs):
        self.prefix = kwargs.pop("prefix", "")
        self.on_input = kwargs.pop("on_input", None)

        QtGui.QFrame.__init__(self, *args, **kwargs)

        self.chat_text = ChatText()
        self.input = Input()

        if self.on_input is not None:
            self.input.returnPressed.connect(lambda s:self.on_input(self, s))

        gl = QtGui.QGridLayout(self)
        gl.addWidget(self.chat_text, 0, 0)
        gl.addWidget(self.input, 1, 0)


class Gui(QtGui.QTabWidget):
    def __init__(self, *args, **kwargs):
        QtGui.QTabWidget.__init__(self, *args, **kwargs)
        self.setMovable(True)
        self.sub_palette = self.palette()

    def set_color(color_role, color):
        for i in range(self.count()):
            with self.widget(i) as t:
                for w in (t.chat_text, t.input):
                    self.sub_palette.setColor(color_role, color)
                    w.setPalette(self.sub_palette)


if __name__ == "__main__":
    import sys

    def yoba(owner, text):
        owner.chat_text.append(text)
        cl.append(text)
        com.model().setStringList(cl)

    app = QtGui.QApplication(sys.argv)
    cl = ["aab", "aac", "aad"]
    com = QtGui.QCompleter(cl)
    g = Gui()
    g.addTab(Tab(on_input=yoba), "main")
    com.setWidget(g.widget(0).input)
    com.setCompletionMode(QtGui.QCompleter.PopupCompletion)
    com.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
    g.show()
    sys.exit(app.exec_())
