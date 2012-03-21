#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" RedirectPlugin.py


"""

import re
import urlparse

try:
    # support for python 3 in the future
    from http.client import HTTPConnection
except:
    # for python 2
    from httplib import HTTPConnection

class RedirectPlugin(object):
    def __init__(self):
        self.__name = ''
        self.__maxRedirectCount = 2
        self.__redirect = {}

    def Initialize(self, runner, name, param):
        self.__name = name
        self.__maxRedirectCount = 5

        if 'MaxRedirectCount' in param:
            self.__maxRedirectCount = param['MaxRedirectCount']

        runner.AddEnqueHook(self.Enque)
        
    def Enque(self, entry):
        ut = urlparse.urlparse(entry.link)
        if ut.netloc in self.__redirect:
            if not self.__redirect[ut.netloc]:
                # already known as no redirect
                return
            entry.link = self._Traverse(entry.link)
        else:
            link = self._Traverse(entry.link)
            if link != entry.link:
                self.__redirect[ut.netloc] = True
                entry.link = link
            else:
                self.__redirect[ut.netloc] = False

    def _Traverse(self, link):
        for i in range(self.__maxRedirectCount):
            res = self._GetHead(link)
            if res is not None and (res.status == 301 or res.status == 302):
                # if moved or found, traverse location
                loc = res.getheader('location', link)
                ut = urlparse.urlparse(loc)
                if ut.netloc == '':
                    # relative
                    nx = urlparse.urljoin(link, loc)
                else:
                    nx = loc
                if nx == link:
                    return link
                else:
                    link = nx
            else:
                return link
        return link

    def _GetHead(self, link):
        ut = urlparse.urlparse(link)

        con = HTTPConnection(ut.netloc)
        res = None
        try:
            path = ut.path
            if ut.params != '':
                path += ';' + ut.params
            if ut.query != '':
                path += '?' + ut.query
            con.request('HEAD', path)
            res = con.getresponse()
        except:
            res = None
        finally:
            con.close()
        return res

PLUGIN = RedirectPlugin

def RedirectPluginTest():
    plugin = RedirectPlugin()

    class DummyEntry(object):
        def __init__(self, link):
            self.link = link

    links = ["http://feeds.wired.com/~r/wired/index/~3/9Gl5lJNbgvM/", "http://www.4gamer.net/games/038/G003857/20120223012/", "http://distrowatch.com/7125"]

    for link in links:
        entry = DummyEntry(link)
        print entry.link
        plugin.Enque(entry)
        print entry.link
        entry.link = link
        print entry.link
        plugin.Enque(entry)
        print entry.link


if __name__ == "__main__":
    RedirectPluginTest()
