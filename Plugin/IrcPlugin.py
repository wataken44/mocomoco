#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" IrcPlugin.py


"""

# twisted imports
from twisted.words.protocols import irc
from twisted.internet import reactor, protocol
from twisted.python import log

# system imports
import sys
import datetime
import time

from threading import Thread, Lock

class IrcPlugin(object):
    def __init__(self):
        pass

    def Initialize(self, runner, name, param):
        self.__name = name
        runner.AddProcessHook(self.Process)

        # initialize message queue
        runIntervalSec = 720
        if 'RunIntervalSec' in param:
            runInterval = int(param['RunIntervalSec'])

        messageIntervalSec = 5
        if 'MessageIntervalSec' in param:
            messageInterval = int(param['MessageIntervalSec'])

        qt = QueueThread(runIntervalSec, messageIntervalSec)
        self.__queue = qt
        runner.AddThread(qt)

        # initialize bot
        server = param['Server']
        port = 6667
        if 'Port' in param:
            port = int(param['Port'])
        channel = param['Channel'].encode("utf-8")
        if channel[0] != '#':
            channel = "#" + channel

        factory = MocoBotFactory(channel, qt)

        tt = TwistedThread(server, port, factory)
        runner.AddThread(tt)

    def Process(self, entry):
        msg = ["[%s]" % entry.sourceTitle, entry.title, entry.link]

        while len(msg) > 0:
            buf = ""
            while len(msg) > 0:
                if buf == "":
                    buf = msg[0]
                    msg.pop(0)
                    continue

                if len(buf.encode("utf-8")) + len(msg[0].encode("utf-8")) < 480:
                    if buf != "":
                        buf += " "
                    buf = buf + msg[0]
                    msg.pop(0)
                    continue
                break
                    
            if len(buf.encode("utf-8")) >= 480:
                tmp = ""
                for k in reversed(range(len(buf))):
                    tmp = buf[0:k] + "<truncated>"
                    if(len(tmp.encode("utf-8")) < 480):
                        break
                buf = tmp

            self.__queue.Enque(buf)

class QueueThread(Thread):
    def __init__(self, runIntervalSec, messageIntervalSec):
        Thread.__init__(self)
        Thread.setDaemon(self, True)
        
        self.__queue = []
        self.__lock = Lock()

        self.__runIntervalSec = runIntervalSec
        self.__messageIntervalSec = messageIntervalSec

        self.__bot = None

    def RegisterBot(self, bot):
        self.__bot = bot

    def Enque(self, message):
        self._Lock()
        self.__queue.append(message)
        self._Unlock()

    def Start(self):
        Thread.start(self)

    def Stop(self):
        pass

    def Join(self):
        Thread.join(self)

    def _Lock(self):
        self.__lock.acquire()

    def _Unlock(self):
        self.__lock.release()

    def run(self):
        while True:
            while self.__bot is not None:
                msg = None

                self._Lock()
                if len(self.__queue) > 0:
                    msg = self.__queue[0]
                    self.__queue.pop(0)
                self._Unlock()

                if msg is None:
                    break
                else:
                    self.__bot.Say(msg)
               
                time.sleep(self.__messageIntervalSec)

            time.sleep(self.__runIntervalSec)

class TwistedThread(Thread):
    def __init__(self, server, port, factory):
        Thread.__init__(self)
        Thread.setDaemon(self, True)

        self.__server = server
        self.__port = port
        self.__factory = factory

    def Start(self):
        Thread.start(self)

    def Stop(self):
        pass

    def Join(self):
        Thread.join(self)

    def run(self):
        reactor.connectTCP(self.__server, self.__port, self.__factory)
        reactor.run(installSignalHandlers=0)

class MocoBot(irc.IRCClient):
    nickname = "moco"

    def __init__(self, channel, queue):
        self.__channel = channel
        self.__queue = queue
        
    def signedOn(self):
        """Called when bot has succesfully signed on to server."""
        self.join(self.__channel)

    def joined(self, channel):
        self.__queue.RegisterBot(self)
        self.Say(u"こんにちはこんにちは")

    def Say(self, msg):
        self.say(self.__channel, msg.encode('utf-8'))

class MocoBotFactory(protocol.ClientFactory):
    def __init__(self, channel, queue):
        self.__queue = queue
        self.__channel = channel

    def buildProtocol(self, addr):
        protocol = MocoBot(self.__channel, self.__queue)
        return protocol

    def clientConnectionLost(self, connector, reason):
        """If we get disconnected, reconnect to server."""
        print "connection lost:", reason
        time.sleep(10)
        connector.connect()

    def clientConnectionFailed(self, connector, reason):
        print "connection failed:", reason
        reactor.stop()

PLUGIN = IrcPlugin

if __name__ == "__main__":
    pass
