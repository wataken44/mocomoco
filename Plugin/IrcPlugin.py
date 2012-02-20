#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" IrcPlugin.py


"""

# twisted imports
from twisted.words.protocols import irc
from twisted.internet import reactor, protocol
from twisted.python import log

from threading import Thread

# system imports
import sys
import time

class IrcPlugin(object):
    def Initialize(self, runner, name, param):
        self.__name = name
        runner.AddProcessHook(self.Process)

        self.__channel = param['Channel'].encode('utf-8')
        if self.__channel[0] != "#":
            self.__channel = "#" + self.__channel

        self.__factory = MocoBotFactory(self, self.__channel)
        self.__bot = None
        self.__server = param['Server']
        
        reactor.connectTCP(self.__server, 6667, self.__factory)

        self.__thread = TwistedThread()
        runner.AddThread(self.__thread)

    def RegisterBot(self, bot):
        self.__bot = bot
        
    def Process(self, entry):
        if self.__bot is None:
            return

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
            
            self.__bot.notice(self.__channel, buf.encode('utf-8'))

class TwistedThread(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.__finished = False
        Thread.setDaemon(self, True)
        
    def Start(self):
        Thread.start(self)
        time.sleep(5)

    def Stop(self):
        self.__finished = True

    def Join(self):
        Thread.join(self)

    def run(self):
        reactor.run(installSignalHandlers=0)

class MocoBot(irc.IRCClient):
    nickname = "moco"

    def signedOn(self):
        """Called when bot has succesfully signed on to server."""
        self.join(self.factory.channel)

    def joined(self, channel):
        self.factory.plugin.RegisterBot(self)
        self.notice(self.factory.channel, (u"こんにちはこんにちは").encode('utf-8'))
    
class MocoBotFactory(protocol.ClientFactory):
    def __init__(self, plugin, channel):
        self.__plugin = plugin
        self.__channel = channel

    @property
    def channel(self):
        return self.__channel

    @property
    def plugin(self):
        return self.__plugin

    def buildProtocol(self, addr):
        p = MocoBot()
        p.factory = self
        return p

    def clientConnectionLost(self, connector, reason):
        """If we get disconnected, reconnect to server."""
        print "connection lost:", reason
        connector.connect()
        #reactor.stop()

    def clientConnectionFailed(self, connector, reason):
        print "connection failed:", reason
        reactor.stop()

PLUGIN = IrcPlugin

if __name__ == "__main__":
    pass
