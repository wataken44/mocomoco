#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" moco.py


"""

import codecs
import getopt
import sys

from Moco.MocoRunner import MocoRunner

def main():
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout)

    opts, args = getopt.gnu_getopt(sys.argv[1:], 'c:o:')

    config = "config.json"
    offset = 180
    for o, a in opts:
        if o == '-c':
            config = a
        if o == '-o':
            offset = int(a)

    runner = MocoRunner()
    runner.LoadConfigFile(config)
    runner.LoadAccount()
    runner.LoadPlugin()

    runner.SetOffset(offset)
    runner.IgnoreSIGHUP()
    runner.Run()


if __name__ == "__main__":
    main()
