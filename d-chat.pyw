import sys
import gui
import bnet
import platform
import itertools
import PySide
from PySide import QtGui, QtCore


print(platform.python_version())
print(PySide.__version__)
print(PySide.QtCore.__version__)
print(platform.system())

class Dchat():
    def __init__(self, host, port):
        self.account = None
        self.password = None
        self.channel = ""
        self.nicknames = {}

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
        if packet.event_id in ("ID_USER", "ID_JOIN", "ID_USERFLAGS"):
            acc = str(packet.username, "utf-8")
            nick = ""
            text = str.join("", map(chr, itertools.takewhile(lambda ch: ch < 128, packet.text)))
            if str.startswith(text, "PX2D"):
                text = text.split(",")
                if len(text) >= 2:
                    nick = text[1]

            self.nicknames[acc] = nick
            #self.autocomplete_dictionary.add(acc)

        elif packet.event_id in ("ID_LEAVE",):
            uname = str(packet.username, "utf-8")
            if uname in self.nicknames:
                del self.nicknames[uname]

        elif packet.event_id in ("ID_INFO",):
            self.main_tab.chat_text.append(str(packet.text, "utf-8"))
            #self.push(("system", str(packet.text, "utf-8")))

        elif packet.event_id in ("ID_ERROR",):
            self.main_tab.chat_text.append(str(packet.text, "utf-8"))
            #self.push(("red", str(packet.text, "utf-8")))

        elif packet.event_id in ("ID_TALK", "ID_EMOTE"):
            self.main_tab.chat_text.append(str(packet.text, "utf-8"))
            '''acc = str(packet.username, "utf-8")
            nick = self.nicknames.get(acc, "")
            self.push(
                ("nickname", nick),
                ("delimiter", "*"),
                ("nickname", acc),
                ("delimiter", ": "),
                ("text", str(packet.text, "utf-8")),
            )

            self.trade.activity_triggered()'''

        elif packet.event_id in ("ID_CHANNEL",):
            self.channel = str(packet.text, "utf-8")
            self.nicknames.clear()

        elif packet.event_id in ("ID_WHISPER",):
            acc = str(packet.username, "utf-8")
            nick = self.nicknames.get(acc, "")
            self.push(
                ("whisper nickname", nick),
                ("delimiter", "*"),
                ("whisper nickname", acc),
                ("delimiter", " -> "),
                ("whisper nickname", "*" + self.account),
                ("delimiter", ": "),
                ("whisper", str(packet.text, "utf-8")),
                whisper=True,
            )

        elif packet.event_id in ("ID_WHISPERSENT",):
            acc = str(packet.username, "utf-8")
            nick = self.nicknames.get(acc, "")
            self.push(
                ("whisper nickname", "*" + self.account),
                ("delimiter", " -> "),
                ("whisper nickname", nick),
                ("delimiter", "*"),
                ("whisper nickname", acc),
                ("delimiter", ": "),
                ("whisper", str(packet.text, "utf-8")),
                whisper=True,
            )

        elif packet.event_id in ("ID_BROADCAST",):
            acc = str(packet.username, "utf-8")
            self.push(
                ("whisper nickname", acc),
                ("delimiter", ": "),
                ("whisper", str(packet.text, "utf-8")),
                whisper=True,
            )

        else:
            logging.info(str.format("[d-chat.py] unhandled chat event\n{}", packet))


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)

    dchat = Dchat("rubattle.net", 6112)
    dchat.bnet.login("pohmelie9", "chat")

    sock_notifier = QtCore.QSocketNotifier(dchat.bnet.sock.fileno(), QtCore.QSocketNotifier.Read)
    sock_notifier.activated.connect(dchat.bnet.on_packet)

    sys.exit(app.exec_())
