#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" MocoRunner.py


"""

import glob
import imp
import json
import os
import re
import signal
import time

import Plugin

from datetime import datetime, timedelta
from math import floor, ceil

from pit import Pit
from GoogleReader.GoogleReaderApi import GoogleReaderApi
from Moco import MocoParser

class MocoRunner(object):
    def __init__(self):
        self.__config = {
            'EntryCountPerRequest' : 20,
            'Plugin' : [],
            'ProfileSuffix' : 'moco',
            'QueueDepth' : 512,
            'ReconnectIntervalSec' : 1800,
            'RequestIntervalSec' : 5,
            'RunIntervalSec' : 600,
            'UpdateTokenIntervalSec' : 1200
            }
        self.__api = None
        self.__offset = 0

        self.__thread = []
        self.__enqueHook = []
        self.__filterHook = []
        self.__processHook = []
        self.__dequeHook = []
    
    @property
    def config(self):
        return self.__config

    @property
    def api(self):
        return self.__api

    @property
    def email(self):
        return self.__email

    @property
    def password(self):
        return self.__password

    def LoadConfigFile(self, filename):
        fp = open(filename)
        config = json.load(fp, 'utf-8')
        fp.close()
        self.LoadConfig(config)

    def LoadConfig(self, config):
        self.__config.update(config)

        for k in self.__config.keys():
            type(self).__setattr__(self, k[0].lower()+k[1:], self.__config[k])

    def LoadAccount(self, suffix = None):
        if suffix is None:
            suffix = self.__config['ProfileSuffix']

        profile = 'moco-google-reader-' + suffix
        account = Pit.get(profile,
                          {'require': {'Email': '', 'Password': ''}})
        self.__email = account['Email']
        self.__password = account['Password']

        self.__api = GoogleReaderApi("MocoClient")
        self.api.Connect(self.email, self.password)

    def LoadPlugin(self, pluginDir = None):
        if pluginDir is None:
            pluginDir = ["Plugin"]

        for param in self.plugin:
            pluginName = param['name']
            pluginType = param['plugin']
            pluginParam = param['param']
            
            moduleName = "Plugin." + pluginType
            fp = None
            try:
                fp, pathName, description = imp.find_module(pluginType, pluginDir)
            except:
                print("plugin not found. skipped.(%s in %s)" % (pluginType, ",".join(pluginDir)))

            if fp is None:
                continue

            module = None

            try:
                module = imp.load_module(moduleName, fp, pathName, description)
            finally:
                fp.close()
            
            if module is None:
                continue

            plugin = module.PLUGIN()
            plugin.Initialize(self, pluginName, pluginParam)
                      

    def IgnoreSIGHUP(self, on = True):
        if on:
            signal.signal(signal.SIGHUP, signal.SIG_IGN)
        else:
            signal.signal(signal.SIGHUP, signal.SIG_DFL)

    def SetOffset(self, offset):
        self.__offset = offset

    def Run(self):
        self._Initialize()
        self._Run()
        self._Finish()

    def AddEnqueHook(self, function):
        self.__enqueHook.append(function)

    def AddFilterHook(self, function):
        self.__filterHook.append(function)
    
    def AddProcessHook(self, function):
        self.__processHook.append(function)
    
    def AddDequeHook(self, function):
        self.__dequeHook.append(function)

    def AddThread(self, thread):
        self.__thread.append(thread)

    def _Initialize(self):        
        self.__runTimer = MocoTimer()
        self.__requestTimer = MocoTimer()
        self.__reconnectTimer = MocoTimer()
        self.__updateTokenTimer = MocoTimer()

        ago = datetime.utcnow() - timedelta(0, self.__offset)
        self.__lastTimestampMsec = self.api.GetTimestampFromDate(ago) * 1000

        self.__queue = []

        for thread in self.__thread:
            thread.Start()

    def _Finish(self):
        for thread in self.__thread:
            thread.Stop()

        for thread in self.__thread:
            thread.Join()

    def _Run(self):
        self.__reconnectTimer.Tick()
        
        while True:
            self.__runTimer.Tick()

            tokenLifeTime = int(ceil(self.__updateTokenTimer.Get()))
            if tokenLifeTime > self.updateTokenIntervalSec:
                # update token
                self.api.GetToken()
                self.__updateTokenTimer.Tick()

            # issue request
            self._Request()

            # wait for next iteration
            runTime = int(ceil(self.__runTimer.Get()))
            if runTime < self.runIntervalSec:
                time.sleep(self.runIntervalSec - runTime)

            # reconnect and update session
            connectTime = int(ceil(self.__reconnectTimer.Get()))
            if connectTime > self.reconnectIntervalSec:
                self.api.Reconnect()
                self.__reconnectTimer.Tick()

    def _Request(self):
        entryCount = self.entryCountPerRequest

        for i in range(16):
            self.__requestTimer.Tick()
            
            startTime = self.__lastTimestampMsec / 1000

            feed = self.api.GetAtomByState(
                "reading-list",
                entryCount,
                "o",
                startTime)
            entries = MocoParser.ParseString(feed)
            entries.sort()

            maxTimestampMsec = self.__lastTimestampMsec

            for entry in entries:
                newEntry = True
                if entry.crawlTimestampMsec <= self.__lastTimestampMsec:
                    if entry in self.__queue:
                        newEntry = False
                if newEntry:
                    self._Add(entry)
                else:
                    continue

                maxTimestampMsec = max(maxTimestampMsec, entry.crawlTimestampMsec)

            self.__lastTimestampMsec = maxTimestampMsec

            if len(entries) < entryCount:
                # reached newest entry
                return

            if len(entries) > 0:
                if entries[0].crawlTimestampMsec / 1000 == self.__lastTimestampMsec / 1000:
                    entryCount *= 2

            requestTime = int(ceil(self.__requestTimer.Get()))
            if requestTime < self.requestIntervalSec:
                time.sleep(self.requestIntervalSec - requestTime)

    def _Add(self, entry):
        self._Enque(entry)

        self.__queue.append(entry)

        if not self._Filter(entry):
            self._Process(entry)

        if len(self.__queue) > self.queueDepth:
            front = self.__queue.pop(0)
            self._Deque(front)

    def _Enque(self, entry):
        for function in self.__enqueHook:
            function(entry)

    def _Filter(self, entry):
        for function in self.__filterHook:
            r = function(entry)
            if r:
                return True
        return False

    def _Process(self, entry):
        for function in self.__processHook:
            function(entry)
        
    def _Deque(self, entry):
        for function in self.__dequeHook:
            function(entry)

class MocoTimer(object):
    def __init__(self):
        self.__ticked = datetime.now()

    def Get(self):
        now = datetime.now()
        diff = now - self.__ticked
        return diff.seconds * 1.0 + diff.microseconds / 1000000.0

    def Tick(self):
        now = datetime.now()
        diff = now - self.__ticked
        self.__ticked = now
        return diff.seconds * 1.0 + diff.microseconds / 1000000.0
        

if __name__ == "__main__":
    pass
