#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" AutoReadPlugin.py


"""

import re

class AutoReadPlugin(object):
    def __init__(self):
        self.__name = ''

    def Initialize(self, runner, name, param):
        self.__name = name

        self.__enable = True
        if 'Enable' in param and param['Enable'] == 'false':
            self.__enable = False

        self.__readAtDeque = True
        if 'Timing' in param and param['Timing'] == 'Enque':
            self.__readAtDeque = False

        if self.__enable:
            if self.__readAtDeque:
                runner.AddDequeHook(self.Deque)
            else:
                runner.AddProcessHook(self.Process)

        self.__api = runner.api
        
    def Process(self, entry):
        self._Read(entry)

    def Deque(self, entry):
        self._Read(entry)

    def _Read(self, entry):
        id = entry.id
        
        ret = self.__api.PostEditTag(id, add='user/-/state/com.google/read')
        print ret

PLUGIN=AutoReadPlugin

if __name__ == "__main__":
    pass
