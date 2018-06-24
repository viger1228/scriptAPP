#!/usr/bin/env python3
# coding: UTF-8
# file: tool.py
# author: walker

"""
2018-05-19: Add HTTP rsponse Code
2018-02-15: Add class Crypto
2018-01-23: Add sys.path[0] for log path 
2018-01-16: init

"""

import os
import sys
import time
import base64
import logging

from datetime import datetime
from Crypto.Cipher import AES

logger = ''

http_msg = {
    200: 'OK',
    204: 'No Content',
    400: 'Bad Request',
    401: 'Unauthorized',
    404: 'Not Found',
    405: 'Method Not Allowed',
    500: 'Internal Server Error',
}

def parse_cookie(cookies):
    cook_list = []
    for cookie in cookies.split(','):
        datas = cookie.split(';')
        cooks = {
            'key': datas[0].strip().split('=')[0],
            'value': datas[0].strip().split('=')[1],
        }
        if len(datas) > 1:
            for item in datas[1:]:
                item = item.strip()
                items = item.split('=')
                key = items[0].lower().replace('-','_')
                if len(items) == 2:
                    try:
                        cooks[key] = int(items[1])
                    except ValueError:
                        cooks[key] = str(items[1])
                elif len(items) == 1:
                    cooks[key] = True
        cook_list.append(cooks)
    return cook_list

def timer(func):
    def wrap(*args, **kwargs):
        s_time = time.time()
        rsp = func(*args, **kwargs)
        e_time = time.time()
        msg = '%0.2f sec'%(e_time - s_time)
        if logger:
            logger.info(msg)
        else:
            print(msg)
        return rsp
    return wrap

class Log(object):
    PATH = sys.path[0] + '/logs/'
    LOG_FILE = '%s%s.log'%(PATH,datetime.now().strftime('%Y%m%d'))

    def __init__(self):
        pass

    def get_level(self, level):
        if level == 'debug':
            rep = logging.DEBUG
        elif level == 'info':
            rep = logging.INFO
        elif level in ['warnning','warn']:
            rep = logging.WARN
        elif level == 'error':
            rep = logging.ERROR
        elif level == 'critical':
            rep = logging.CRITICAL
        return rep

    def file_handler(self, logfile=LOG_FILE):
        if not os.path.isdir(self.PATH):
            os.makedirs(self.PATH)
        _format = '[%(asctime)s][%(levelname)s][%(filename)s(line:%(lineno)d)] - %(message)s'
        handler = logging.FileHandler(logfile)
        formatter = logging.Formatter(_format)
        handler.setFormatter(formatter)
        return handler

    def stream_handler(self):
        _format = '[%(asctime)s][%(levelname)s][%(filename)s(line:%(lineno)d)] - %(message)s'
        handler = logging.StreamHandler()
        formatter = logging.Formatter(_format)
        handler.setFormatter(formatter)
        return handler

    def print_handler(self):
        _format = '%(message)s'
        handler = logging.StreamHandler()
        formatter = logging.Formatter(_format)
        handler.setFormatter(formatter)
        return handler

    def file_logger(self, obj='__main__', level='info', logfile=LOG_FILE):
        handler = self.file_handler(logfile)
        logger = logging.getLogger(obj)
        logger.setLevel(self.get_level(level))
        logger.addHandler(handler)
        return logger
    
    def stream_logger(self, obj='__main__', level='info'):
        handler = self.stream_handler()
        logger = logging.getLogger(obj)
        logger.setLevel(self.get_level(level))
        logger.addHandler(handler)
        return logger

    def print_logger(self, obj='__main__', level='info'):
        handler = self.print_handler()
        logger = logging.getLogger(obj)
        logger.setLevel(self.get_level(level))
        logger.addHandler(handler)
        return logger

class Crypto(object):
    IV = 16 * '\x00'
    def encode(self, msg, key=b'@'*16):
        data = self.encrypt(msg, key)
        pwd = base64.encodestring(data)
        return pwd

    def decode(self, pwd, key=b'@'*16):
        data = base64.decodestring(pwd)
        msg = self.decrypt(data, key)
        return msg

    def encrypt(self, msg, key):
        data = self.fill(msg)
        cryptor = AES.new(key, AES.MODE_CBC, self.IV)
        return cryptor.encrypt(data)
    
    def decrypt(self, data, key):
        cryptor = AES.new(key, AES.MODE_CBC, self.IV)
        msg = self.drain(cryptor.decrypt(data))
        return msg
    
    def fill(self, data, key=b'$@#@$'):
        msg = '%d%s'%(len(data),key) + data
        n = (16 - (len(msg) % 16))
        if n != 0:
            msg += '#' * n
        return msg
    
    def drain(self, data, key=b'$@#@$'):
        n, msg = data.split(key,1)
        return msg[:int(n)]

if __name__ == '__main__':

   msg = sys.argv[1]
   crypto = Crypto()
   pwd = crypto.encode(msg).strip()
   msg = crypto.decode(pwd)
   print(pwd)
   print(msg)
