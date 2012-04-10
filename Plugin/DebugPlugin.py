#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" DebugPlugin.py


"""

import codecs

class DebugPlugin(object):
    def __init__(self):
        self.__name = ''

    def Initialize(self, runner, name, param):
        self.__name = name
        self.__enable = True
        if param['Enable'] == 'false' :
            self.__enable = False

        if self.__enable:
            runner.AddEnqueHook(self.Enque)
            runner.AddFilterHook(self.Filter)
            runner.AddProcessHook(self.Process)
            runner.AddDequeHook(self.Deque)
        
    def Enque(self, entry):
        pass

    def Filter(self, entry):
        return False

    def Process(self, entry):
        s = str(entry)
        print s.decode('utf-8')

    def Deque(self, entry):
        pass

PLUGIN = DebugPlugin

if __name__ == "__main__":
    pass
