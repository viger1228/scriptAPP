#!/usr/bin/env python3
# file: mod.py
# author: walker

"""
Changelogs

2018.06.24: init

"""
import os
import sys
import traceback

import tool

class Script(object):

    def __init__(self, logger):
        self.logger = logger
        tool.logger = logger

    @tool.timer
    def run(self, **kwargs):
        self.args = kwargs
        try:
            func = getattr(self, self.args['function'])
            func()
        except Exception:
            error = traceback.format_exc()
            self.logger.error(error)

    def get_func(self):
        func = []
        for n in dir(self):
            if n in ['run', 'get_func']: continue
            if n.find('__') == 0: continue
            if n.find('Mod') >= 0: continue
            if not callable(getattr(self, n)): continue
            func.append(n)
        return func
