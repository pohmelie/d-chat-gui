class AutoTrade():
    TRADE_INFO_FORMAT = "Trade info:\nmessage = {message}\ntimeout = {current_time}/{timeout}\n"

    def __init__(self, say, loop):
        self.trade_message = None
        self.trade_timeout = None

        self.say = say
        self.loop = loop
        self.activity = True
        self.started = False
        self.stopping = False
        self.current_time = 0

        self.commands = {
            "\\trade-message": self.command_trade_message,
            "\\trade-timeout": self.command_trade_timeout,
            "\\trade-start": self.command_trade_start,
            "\\trade-stop": self.command_trade_stop,
            "\\trade-info": self.command_trade_info,
        }

    def activity_triggered(self):
        self.activity = True

    def command_trade_info(self, msg):
        '''
        \\trade-info
            Show current trade information.
        '''

        info = str.format(
                AutoTrade.TRADE_INFO_FORMAT,
                message=self.trade_message,
                current_time=self.current_time,
                timeout=self.trade_timeout
            )

        for s in info.split("\n"):
            self.say("\\echo " + s)

    def command_trade_message(self, msg):
        '''
        \\trade-message [message]
            Set new trade message. Show current trade message if parameters are omitted.
        '''
        if len(str.split(msg)) == 1:
            self.say(str.format("\\echo Current trade-message = {}", self.trade_message))
        else:
            self.trade_message = str.strip(msg[str.index(msg, " "):])

    def command_trade_timeout(self, msg):
        '''
        \\trade-timeout [seconds]
            Set new trade timeout in seconds. Show current trade timeout if parameters are omitted.
        '''
        if len(str.split(msg)) == 1:
            self.say(str.format("\\echo Current trade-timeout = {}", self.trade_timeout))
        else:
            _, x, *rest = str.split(msg)
            if str.isdecimal(x):
                self.trade_timeout = int(x)
            else:
                self.say(str.format("\\echo Bad parameter '{}'. Should be positive integer", x))

    def command_trade_start(self, msg):
        '''
        \\trade-start
            Start trade timer.
        '''
        if self.started:
            self.say("\\echo Autotrade already started")
            return

        if self.trade_message is None:
            self.say("\\echo Trade message should be setted with \\trade-message")
        elif self.trade_timeout is None:
            self.say("\\echo Trade timeout should be setted with \\trade-timeout")
        else:
            self.say("\\echo Autotrade started")
            self.started = True
            self.activity = False
            self.current_time = 0
            self.loop.set_alarm_in(1, self.callback)

    def command_trade_stop(self, msg):
        '''
        \\trade-stop
            Stop trade timer.
        '''
        if self.started:
            self.say("\\echo Stopping autotrade...")
            self.stopping = True
        else:
            self.say("\\echo Autotrade not started")

    def callback(self, loop, user_data):
        if self.stopping:
            self.say("\\echo Autotrade stopped")
            self.started = False
            self.stopping = False

        elif self.started:
            self.current_time = self.current_time + 1
            if self.activity:
                if self.current_time >= self.trade_timeout:
                    self.current_time = 0
                    self.activity = False
                    self.say(self.trade_message)

            self.loop.set_alarm_in(1, self.callback)
