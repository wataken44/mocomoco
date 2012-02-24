#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" BitlyPlugin.py


"""

import json
import urllib
import urllib2

from pit import Pit

class BitlyPlugin(object):
    __URL_BASE = 'https://api-ssl.bitly.com'
    __API_PATH_SHORTEN = '/v3/shorten'

    def __init__(self):
        self.__name = ''

    def Initialize(self, runner, name, param):
        self.__name = name
        
        suffix = param['ProfileSuffix']

        account = Pit.get('moco-bitly-plugin-' + suffix,
                          {'require' : {'Login': '', 'ApiKey' : ''}})

        self.__login = account['Login']
        self.__apiKey = account['ApiKey']

        runner.AddEnqueHook(self.Enque)

    def Enque(self, entry):
        param = {
            "format" : "json",
            "login" : self.__login,
            "apiKey" : self.__apiKey,
            "longUrl" : entry.link,
            "domain" : "j.mp"
            }
        url = self.__URL_BASE + self.__API_PATH_SHORTEN
        url += "?" + urllib.urlencode(param)

        ret = None
        try:
            fp = urllib.urlopen(url)
            ret = json.loads(fp.read())
        except:
            pass

        if ret:
            if ret['status_txt'] == 'OK':
                entry.link = ret['data']['url']
            else:
                print ret

PLUGIN = BitlyPlugin

if __name__ == "__main__":
    pass
