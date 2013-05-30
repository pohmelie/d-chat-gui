#!/usr/bin/python3

import bnet
import tui
import urwid
import logging
import sys
import time
import itertools
import collections
import inspect
import autotrade


class Dchat():
    DEFAULT_TITLE_FORMAT = "{channel} ({ppl}) [{shift}/{lines}]"

    HOTKEYS_HELP = (
        ("ctrl-x", "Exit."),
        ("ctrl-w", "Switch between 'all-messages' mode and 'whispers-only' mode."),
        ("up/down", "Browse commands history."),
        ("ctrl-up/ctrl-down/page up/page down/ctrl-home/ctrl-end", "Chat navigation."),
        ("ctrl-r", "Reload 'd-chat.init' file."),
        ("ctrl-t", "Show trade information. (\\trade-info command)"),
        ("tab", "Autocomplete word. It's works for commands and in-chat account names."),
        ("f1", "Show this help."),
    )

    LOGO = '''
    ##
    ##
######     ##### ## ##  #### ######
##  ## ### ##    ##### ##-##   ##
######     ##### ## ## ## ##   ##'''

    def __init__(self, host, port):
        self.account = None
        self.password = None
        self.channel = ""

        self.bnet = bnet.Bnet(host, port, self.login_error, self.chat_event)
        self.tui = tui.Tui()

        self.nicknames = {}
        self.autocomplete_dictionary = set()
        self.commands_history = collections.deque(maxlen=20)
        self.commands_history_index = None

        self.sock_handle = None

        self.commands = {
            "\\echo": self.echo,
            "\\reload": self.reload,
            "\\help": self.help,
            "\\connect": self.connect,
            "\\disconnect": self.disconnect,
        }

        self.navigation = {
            "ctrl up": lambda: self.tui.chat.up(),
            "ctrl down": lambda: self.tui.chat.down(),
            "page up": lambda: self.tui.chat.up(10),
            "page down": lambda: self.tui.chat.down(10),
            "ctrl home": lambda: self.tui.chat.home(),
            "ctrl end": lambda: self.tui.chat.end(),
        }

    def run(self):
        self.loop = urwid.MainLoop(
            self.tui.frame,
            palette=self.tui.palette,
            handle_mouse=False,
            unhandled_input=self.on_input
        )

        self.trade = autotrade.AutoTrade(self.say, self.loop)
        self.commands.update(self.trade.commands)

        for line in str.split(Dchat.LOGO, "\n"):
            self.push(("light green", line))

        self.push("")
        self.push(
            ("system", "Welcome to "),
            ("light green", "d-chat"),
            ("system", " — simple battle.net chat.")
        )
        self.push(
            ("system", "Type '"),
            ("red", "\\help"),
            ("system", "' or press '"),
            ("red", "f1"),
            ("system", "' for more information.")
        )
        self.push("")
        self.reload()
        self.loop.run()

    def reload(self, *args):
        '''
        \\reload
            Reloads d-chat.init file. d-chat.init file loads on start and simply executes like user input.
        '''
        try:
            for line in open("d-chat.init"):
                if line.strip() != "":
                    self.say(line.strip())
        except:
            self.say("\\echo Can't open file 'd-chat.init'.")

    def echo(self, msg):
        '''
        \\echo message
            Print message to screen without sending to battle.net.
        '''
        self.push(str.strip(msg[len("\\echo"):]))

    def help(self, *args):
        '''
        \\help
            Show help information.
        '''
        self.push(("red", "Available commands:"))
        for info in map(lambda c: inspect.getdoc(self.commands[c]), sorted(self.commands)):
            comm, *descs = info.split("\n")
            self.push(("system", comm))
            for desc in descs:
                self.push(desc)

        self.push()
        self.push(("red", "Hotkeys:"))
        for key, desc in Dchat.HOTKEYS_HELP:
            self.push(("system", key))
            self.push("    " + desc)

    def connect(self, msg=""):
        '''
        \\connect [account] [password]
            Disconnect if connected and connect to battle.net. Using previous sucessful 'account' and 'password' if parameters are omitted.
        '''
        self.disconnect()
        msg = msg.split()
        if len(msg) < 3 and self.account is None:
            self.say("\\echo Can't connect without account name and password. Type '\\help' for more information.")
        else:
            if len(msg) >= 3:
                self.account = msg[1]
                self.password = msg[2]

            self.bnet.login(self.account, self.password)
            self.sock_handle = self.loop.watch_file(self.bnet.sock, self.bnet.on_packet)
            self.say("\\echo Connecting...")

    def disconnect(self, *args):
        '''
        \\disconnect
            Disconnect from battle.net.
        '''
        if self.sock_handle:
            self.loop.remove_watch_file(self.sock_handle)
            self.sock_handle = None
            self.bnet.sock.close()
            self.say("\\echo Disconnected.")

    def say(self, msg):
        if str.startswith(msg, "\\"):
            for command in self.commands:
                if str.startswith(msg, command):
                    self.commands[command](msg)
                    break
            else:
                self.say(str.format("\\echo Unknown command '{}'.", msg))

        elif self.sock_handle is not None:
            for i in range(0, len(msg), 200):
                submsg = msg[i:i + 200]
                self.bnet.say(submsg)

                if not str.startswith(submsg, "/"):
                    self.push(
                        ("delimiter", "*"),
                        ("nickname", self.account),
                        ("delimiter", ": "),
                        ("text", submsg),
                    )

    def on_input(self, key):
        if key in self.navigation:
            self.navigation[key]()
            self.tui.chat.refresh()

        elif key == "enter":
            msg = self.tui.inpu.get_edit_text()
            if len(msg.strip()) > 0:
                self.commands_history.appendleft(msg)
                self.commands_history_index = None
                self.say(msg)
                self.tui.inpu.set_edit_text("")

        elif key == "ctrl x":
            raise urwid.ExitMainLoop()

        elif key == "ctrl w":
            self.tui.chat.switch()

        elif key == "ctrl r":
            self.reload()

        elif key == "ctrl t":
            self.say("\\trade-info")

        elif key == "tab":
            self.autocomplete()

        elif key == "up":
            if len(self.commands_history) != 0:
                if self.commands_history_index is None:
                    self.commands_history_index = 0
                else:
                    self.commands_history_index = min(self.commands_history_index + 1, len(self.commands_history) - 1)

                self.tui.inpu.set_edit_text("")
                self.tui.inpu.insert_text(self.commands_history[self.commands_history_index])

        elif key == "down":
            if self.commands_history_index == 0:
                self.commands_history_index = None
                self.tui.inpu.set_edit_text("")

            elif self.commands_history_index is not None:
                self.commands_history_index = max(self.commands_history_index - 1, 0)
                self.tui.inpu.set_edit_text("")
                self.tui.inpu.insert_text(self.commands_history[self.commands_history_index])

        elif key == "f1":
            self.help()

        self.refresh_title()

    def push(self, *args, **kwargs):
        if kwargs.get("whisper", False):
            color = "whisper time"
        else:
            color = "time"

        def f(el):
            if isinstance(el, tuple):
                el = el[1]
            return len(el) > 0

        args = tuple(filter(f, args))
        self.tui.chat.push((color, time.strftime("[%H:%M:%S] ")), *args, **kwargs)

    def login_error(self, packet_id, retcode=None):
        if retcode is None:
            msg = str.format("Error on '{}'.", packet_id)
        else:
            msg = str.format("Error on '{}' with retcode = {}.", packet_id, retcode)

        self.push(("red", msg))

        if retcode == 1:
            self.push(("red", "Account doesn't exist."))
        elif retcode == 2:
            self.push(("red", "Wrong password."))

        self.disconnect()

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
            self.autocomplete_dictionary.add(acc)

        elif packet.event_id in ("ID_LEAVE",):
            uname = str(packet.username, "utf-8")
            if uname in self.nicknames:
                del self.nicknames[uname]

        elif packet.event_id in ("ID_INFO",):
            self.push(("system", str(packet.text, "utf-8")))

        elif packet.event_id in ("ID_ERROR",):
            self.push(("red", str(packet.text, "utf-8")))

        elif packet.event_id in ("ID_TALK", "ID_EMOTE"):
            acc = str(packet.username, "utf-8")
            nick = self.nicknames.get(acc, "")
            self.push(
                ("nickname", nick),
                ("delimiter", "*"),
                ("nickname", acc),
                ("delimiter", ": "),
                ("text", str(packet.text, "utf-8")),
            )

            self.trade.activity_triggered()

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

        self.refresh_title()

    def refresh_title(self):
        self.tui.chat_box.set_title(
            str.format(
                Dchat.DEFAULT_TITLE_FORMAT,
                channel=self.channel,
                ppl=len(self.nicknames),
                shift=self.tui.chat.shift,
                lines=len(self.tui.chat.lines),
            )
        )

    def autocomplete(self):
        end = self.tui.inpu.get_edit_text()
        for sep in (" ", "*"):
            end = str.split(end, sep)[-1]

        passes = sorted(
            itertools.chain(
                filter(lambda s: str.startswith(s, end), self.commands),
                filter(lambda s: str.startswith(s, end), self.autocomplete_dictionary)
            )
        )

        if len(passes) > 1:
            self.push(("system", str.format("{} possibilities:", len(passes))))
            for word in passes:
                self.push(("autocomplete", word))

        elif len(passes) == 1:
            self.tui.inpu.insert_text(passes[0][len(end):] + " ")


if __name__ == "__main__":
    logging.basicConfig(
        filename="d-chat.log",
        level=logging.INFO,
        format="%(asctime)s %(message)s",
        datefmt="[%H:%M:%S]",
    )

    Dchat("rubattle.net", 6112).run()
