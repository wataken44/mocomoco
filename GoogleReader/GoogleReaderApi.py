#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" GoogleReaderApi.py

Google Reader API class
"""

import calendar
import json
import re
import time
import urllib

from datetime import datetime, timedelta
from gdata.service import GDataService, Query

class GoogleReaderApi(object):
    def __init__(self, client="GoogleReaderAPIClient"):
        self.__service = GDataService(
            account_type='GOOGLE',
            service='reader',
            server='www.google.com',
            source=client)
        self.__client = client
        pass

    def Connect(self, email, password):
        """Connect to google reader"""

        self.__email = email
        self.__password = password

        # login
        self.__service.ClientLogin(email, password)
        # get token
        self.__token = self.__service.Get(
            '/reader/api/0/token',
            converter=lambda x:x)
        
        # get user id
        # ugly way... is there any API?
        ptn = re.compile('user/(\d+)/')

        tagList = json.loads(self.GetTagList())

        # there is at least one tag 'user/<userid>/state/com.google/...'
        mres = ptn.search(tagList['tags'][0]['id'])
        self.__userId = mres.group(1)

    def Reconnect(self):
        self.Connect(self.__email, self.__password)

    def GetToken(self):
        return self.__token

    def GetUserId(self):
        return self.__userId

    def GetTagList(self):
        query = Query(feed='/reader/api/0/tag/list',
                      params={'all':'true', 'output':'json'})
        feed = self.__service.Get(query.ToUri(), converter=lambda x:x)
        return feed

    def GetAtomByState(self,
                       state = "read",
                       count = 20, 
                       order = 'd',
                       startTime = None,
                       excludeTarget = None):
        uri = "".join(['/reader/atom/user/', self.__userId, '/state/com.google/', state])

        params = {
            'n' : str(count),
            'client' : self.__client,
            'r' : order,
            'ck' : self.CreateTimestamp(datetime.utcnow())
            }
        if order == 'o':
            if not startTime:
                # default 1 hour before
                startTime = self.CreateTimestamp(datetime.utcnow() - timedelta(0, 3600))
            params['ot'] = str(startTime)
        if excludeTarget:
            params['xt'] = excludeTarget

        query = Query(feed=uri, params=params)
        feed = self.__service.Get(query.ToUri(), converter = lambda x:x)

        return feed

    def PostEditTag(self, id,
                    add='user/-/state/com.google/read', remove=None,
                    action='edit'):
        params = {
            'i' : id,
            'ac' : 'edit',
            'T' : self.__token
            }
        if add is not None:
            params['a'] = add
        elif remove is not None:
            params['r'] = remove

        uri = '/reader/api/0/edit-tag'
        extra_headers={'Content-Type': 'application/x-www-form-urlencoded'}

        ret = self.__service.Post(
            urllib.urlencode(params), uri,
            converter = lambda x:x,
            extra_headers=extra_headers)
        
        return ret

    def CreateTimestamp(self, date):
        return str(self.GetTimestampFromDate(date))

    def GetTimestampFromDate(self, date):
        return calendar.timegm(date.utctimetuple())

    def GetDateFromTimestamp(self, timestamp):
        return datetime(time.gmtime(timestamp))

if __name__ == "__main__":
    pass
