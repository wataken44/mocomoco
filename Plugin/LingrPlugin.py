#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" LingrPlugin.py


"""

import httplib
import json
import re
import sys
import time
import urllib
import urllib2

from threading import Thread, Lock

from pit import Pit

class LingrPlugin(object):
    def __init__(self):
        self.__name = ''

    def Initialize(self, runner, name, param):
        self.__name = name
        self.__room = param['Room']

        suffix = param['ProfileSuffix']

        account = Pit.get('moco-lingr-plugin-' + suffix,
                          {'require' : {'User': '', 'Password': '', 'AppKey' : ''}})

        self.__lingr = Lingr(account['User'], account['Password'], account['AppKey'])

        runner.AddProcessHook(self.Process)

        self.__thread = LingrThread(self.__lingr)
        runner.AddThread(self.__thread)

    def Process(self, entry):
        msg = "[%s] %s %s" % (entry.sourceTitle, entry.title, entry.link)        
        msg = msg.encode('UTF-8')
        ret = self.__lingr.Say(self.__room, msg)
        if (ret is None) or ('status' not in ret) or (ret['status'] != 'ok'):
            # retry...
            print(ret)
            print(self.__lingr.CreateSession())
            print(self.__lingr.Say(self.__room, msg))

class LingrThread(Thread):
    def __init__(self, lingr):
        Thread.__init__(self)
        self.__lingr = lingr
        self.__finished = False
        Thread.setDaemon(self, True)
        
    def Start(self):
        Thread.start(self)

    def Stop(self):
        self.__finished = True

    def Join(self):
        Thread.join(self)

    def run(self):
        while(True):
            data = self.__lingr.VerifySession()
            if (data is None) or ('status' not in data) or (data['status'] != 'ok'):
                self.__lingr.CreateSession()
            time.sleep(245)
            if self.__finished:
                break

class Lingr(object):
    """ Lingr API Class

    based on pyLingr https://github.com/yoshiori/pyLingr
    """

    __URL_BASE = 'http://lingr.com/api/'
    __URL_OBSERVE = "http://lingr.com:8080/api/"

    def __init__(self, user, password, appKey):
        self.__user = user
        self.__password = password
        self.__counter = 0
        self.__session = None
        self.__nickname = None
        self.__appKey = appKey

        self.__opener = urllib2.build_opener()
        self.__opener.addheaders = [('User-agent', 'Moco Lingr Client(twitter.com/wataken44)')]
        self.__lock = Lock()

    @property
    def user(self):
        return self.__user

    @property
    def password(self):
        return self.__password

    @property
    def opener(self):
        return self.__opener

    @property
    def appKey(self):
        return self.__appKey

    @property
    def session(self):
        return self.__session

    @property
    def nickname(self):
        return self.__nickname

    @property
    def counter(self):
        return self.__counter

    @property
    def lock(self):
        return self.__lock

    def _Lock(self):
        self.lock.acquire()

    def _Unlock(self):
        self.lock.release()

    def _Update(self, data):
        if data is None:
            return
        if ('status' not in data) or (data['status'] != 'ok'):
            return
        if 'session' in data:
            self.__session = data['session']
        if 'nickname' in data:
            self.__nickname = data['nickname']

    def CreateSession(self):
        self._Lock()
        data = self._Post('session/create', {
                'user': self.user,
                'password': self.password,
                'app_key': self.appKey
            })
        self._Update(data)
        self._Unlock()
        return data

    def VerifySession(self):
        self._Lock()
        data = self._Post('session/verify', {
                'session': self.session,            
                'app_key': self.appKey
                })
        self._Update(data)
        self._Unlock()
        return data

    def GetRooms(self):
        self._Lock()
        data = self._Get('user/get_rooms', { 'session': self.session })
        self._Unlock()
        return data

    def Say(self, room, text):
        self._Lock()
        data = self._Post('room/say', {
                'session': self.session,
                'room': room,
                'nickname': self.nickname,
                'text': text})
        self._Unlock()
        return data

    def SubscribeRoom(self, room, reset='true'):
        self._Lock()
        data = self._Post('room/subscribe', {
                'session': self.session,
                'room': room,
                'reset': reset})
        self._Unlock()
        if data is not None and 'counter' in data:
            self.__counter = data['counter']
        return data

    def ObserveEvent(self):
        self._Lock()
        data = self._Get('event/observe', {
                'session': self.session,
                'counter': self.counter})
        self._Unlock()

        if data is not None and 'counter' in data:
            self.__counter = data['counter']
        return data

    def _Post(self, path, param):
        try:
            fp = self.opener.open(self._GetUrl(path), urllib.urlencode(param))
            ret = fp.read()
            fp.close()
            return json.loads(ret)
        except:
            return None

    def _Get(self, path, param = None):
        url = self._GetUrl(path)
        if param is not None:
            url += "?" + urllib.urlencode(param)
        try:
            fp = self.opener.open(url)
            ret = fp.read()
            fp.close()
            return json.loads(ret)
        except:
            return None
        
    def _GetUrl(self, path):
        url = self.__URL_BASE
        if path == 'event/observe':
            url = self.__URL_OBSERVE
        return url + path

PLUGIN = LingrPlugin

def LingrPluginDebug():
    account = Pit.get('moco-lingr-plugin-moco',
                      {'require' : {'User': '', 'Password': '', 'AppKey' : ''}})

    lingr = Lingr(account['User'], account['Password'], account['AppKey'])
    lingr.CreateSession()
    room = 'w5ngr'
    
    for i in range(90):
        ret = lingr.VerifySession()
        msg = "verify %d:" % i + str(ret)
        print msg
        print lingr.Say(room, msg)
        print lingr.Say(room, "a")
        time.sleep(60)

if __name__ == "__main__":
    LingrPluginDebug()
