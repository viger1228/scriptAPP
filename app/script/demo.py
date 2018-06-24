#!/usr/bin/env python3
# file: demo.py
# author: walker

"""
Changelogs

2018.06.24: Add Inheritance
2018.04.19: init

"""
import os
import sys
import argparse
import traceback
from datetime import datetime

sys.path.append('app')
sys.path.append(os.path.dirname(sys.path[0]))

from lib import tool
from lib import mod

class Mod(mod.Script):

    def __init__(self, *args, **kwargs):
        mod.Script.__init__(self, *args, **kwargs)

        # self.args
        # self.logger
        
    def demo(self):
        try:
            message = self.args['message']
        except Exception:
            error = traceback.format_exc()
            self.logger.info(error)
        self.logger.info(message)
        
if __name__ == '__main__':

    os.chdir(sys.path[0])
    logger = tool.Log().stream_logger('info')

    mod = Mod(logger)
    parser = argparse.ArgumentParser()
    parser.add_argument('function', help='{{{}}}'.format('|'.join(mod.get_func())))
    parser.add_argument('--message', metavar='', help='send the message' ,default='Hello')
    args = parser.parse_args()
    kwargs = vars(args)
    
    mod.run(**kwargs)
