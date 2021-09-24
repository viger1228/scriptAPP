#!/usr/bin/env python3
# file: tool.py
# author: walker

"""
Changelogs

2019.01.06: Add Class Netstat
2018.11.03: Add Class Version
2018.11.01: Add Class Args
2018.08.02: Add Timer Func name
2018.07.30: Add String(1m) to seoncd(60)
2018.07.30: Add Rfc3339 format transfer
2018.07.21: Add Base64 encode
2018.07.18: Add excepool
2018.06.05: Add Class Thread
2018.05.28: Add Function baidu_translate
2018.05.19: Add HTTP rsponse Code
2018.03.07: Add Function telegram
2018.02.15: Add Class Crypto
2018.01.23: Add sys.path[0] for log path 
2018.01.16: init

"""

import os
import sys
import pwd
import time
import json
import glob
import copy
import urllib
import base64
import hashlib
import logging
import operator
import httplib2
import traceback
import threading
import subprocess

from subprocess import PIPE
from datetime import datetime, timedelta
from Crypto.Cipher import AES
from bitarray import bitarray

logger = ''

http_msg = {
    200: 'OK',
    204: 'No Content',
    400: 'Bad Request',
    401: 'Unauthorized',
    403: 'Forbidden',
    404: 'Not Found',
    405: 'Method Not Allowed',
    500: 'Internal Server Error',
}

def parse_cookie(cookies):
    cooks = {}
    for cookie in cookies.split(','):
        for item in cookie.split(';'):
            data = item.strip().split('=', 1)
            if len(data) == 2:
                cooks[data[0]] = data[1]
    return cooks

def string_to_second(s):
    unit = {"s": 1, "m": 60, "h": 3600, "d": 86400, "w": 604800}
    rsp = int(s[:-1]) * unit[s[-1]]
    return rsp

def rfc3339_to_datetime(rfc, zone=8):
    if rfc.find('.') >= 0:
        UTC = datetime.strptime(rfc, '%Y-%m-%dT%H:%M:%S.%fZ')
    else:
        UTC = datetime.strptime(rfc, '%Y-%m-%dT%H:%M:%SZ')
    local = UTC + timedelta(hours=zone)
    return local

def rfc3339_to_timestamp(rfc, zone=8):
    local = rfc3339_to_datetime(rfc, zone)
    zero = datetime.fromtimestamp(0)
    timestamp = (local-zero).total_seconds()
    return timestamp

def baidu_translate(en):
    url = 'http://api.fanyi.baidu.com/api/trans/vip/translate'
    key = '7qxfaefI0dTHOba6zK11'
    q = en
    appid = 20180527000167735
    salt = 0
    sign = '{}{}{}{}'.format(appid,q,salt,key).encode('utf8')
    sign = hashlib.md5(sign).hexdigest()
    data = {
      'q': q, 'from': 'en', 'to': 'zh',
      'appid': appid,
      'salt': salt,
      'sign': sign,
    }

    http = httplib2.Http()
    url += '?' + urllib.parse.urlencode(data)
    rspH, rspD = http.request(url, 'GET')
    rspDict = json.loads(rspD)
    return rspDict['trans_result'][0]['dst']

def telegram(reqDict):
    '''
    Send telegram message
    ex:
        data = {'type': 'walker', 'msg': 'Hello',}
        tool.teletgram(data)
    '''    
    url = f'http://{host}/script/telegram.py'
    reqD = urllib.parse.urlencode(reqDict, quote_via=urllib.parse.quote)
    url += '?%s'%(reqD)
    rspH, rspD = httplib2.Http().request(url, 'GET')

# Calculation Time
def timer(func):
    def wrap(*args, **kwargs):
        s_time = time.time()
        rsp = func(*args, **kwargs)
        e_time = time.time()
        msg = '%s %0.4f sec'%(func.__name__, e_time - s_time)
        if logger:
            logger.info(msg)
        else:
            print(msg)
        return rsp
    return wrap

# Add Exception for Function
def excepool(func):
    def wrap(*args, **kwargs):
        rsp = None
        try:
            rsp = func(*args, **kwargs)
        except Exception as e:
            error = traceback.format_exc()
            if logger:
                logger.error(error)
            else:
                print(error)
        return rsp
    return wrap

# Format Print JSON
def json_print(data):
    try:
        if isinstance(data, dict) or isinstance(data, list):
            dict_ = data
        else:
            dict_ = json.loads(data)
        msg = json.dumps(dict_, indent=2, ensure_ascii=False)
        print(msg)
    except Exception as e:
        print(data)

# Version
class Version(object):
 
    def __init__(self):
        info = sys.version_info
        self.ver = '{}.{}.{}'.format(info.major, info.minor, info.micro)

    def compare(self, op, ver):
        m = getattr(operator, op)
        s = [int(n) for n in self.ver.split('.')]
        t = [int(n) for n in ver.split('.')]
        return m(s,t)

# Netstat
class Netstat(object):
    
    PROC_TCP = "/proc/net/tcp"
    STATE = {
        '01':'ESTABLISHED',
        '02':'SYN_SENT',
        '03':'SYN_RECV',
        '04':'FIN_WAIT1',
        '05':'FIN_WAIT2',
        '06':'TIME_WAIT',
        '07':'CLOSE',
        '08':'CLOSE_WAIT',
        '09':'LAST_ACK',
        '0A':'LISTEN',
        '0B':'CLOSING'
    }
    
    def __init__(self):
        pass

    def _load(self):
        with open(self.PROC_TCP,'r') as f:
            content = f.readlines()
            content.pop(0)
        return content
    
    def _hex2dec(self, s):
        return str(int(s,16))
    
    def _ip(self, s):
        ip = [(self._hex2dec(s[6:8])),(self._hex2dec(s[4:6])),
            (self._hex2dec(s[2:4])),(self._hex2dec(s[0:2]))]
        return '.'.join(ip)
    
    def _remove_empty(self, array):
        return [x for x in array if x !='']
    
    def _convert_ip_port(self, array):
        host,port = array.split(':')
        return self._ip(host), self._hex2dec(port)
    
    def _get_pid_of_inode(self, inode):
        for item in glob.glob('/proc/[0-9]*/fd/[0-9]*'):
            try:
                if re.search(inode,os.readlink(item)):
                    return item.split('/')[2]
            except:
                pass
        return None

    def filter(self, **kwargs):
        data = self.netstat()
        for key, val in kwargs.items():
            if val:
                tmp = copy.deepcopy(data)
                data = []
                for n in tmp:
                    if key not in n:
                        data = tmp
                        break
                    elif n[key] == val:
                        data.append(n)
        return data

    def netstat(self):
        content = self._load()
        result = []
        for line in content:
            line_array = self._remove_empty(line.split(' '))
            local_host,local_port = self._convert_ip_port(line_array[1])
            remote_host,remote_port = self._convert_ip_port(line_array[2])
            id_ = line_array[0]
            state = self.STATE[line_array[3]]
            uid = pwd.getpwuid(int(line_array[7]))[0]       
            inode = line_array[9]                           
            pid = self._get_pid_of_inode(inode)                  
            try:                                            
                exe = os.readlink('/proc/'+pid+'/exe')
            except:
                exe = None
            data = {
                'id': id_,
                'uid': uid,
                'local_host': local_host,
                'local_port': local_port,
                'remote_host': remote_host,
                'remote_port': remote_port,
                'state': state,
                'pid': pid,
                'exe': exe,
            }
            result.append(data)
        return result
    

# Parse Argument
class Args(object):

    def __init__(self, data):
        self.data = data
        self.args = {}

    def __getitem__(self, key):
        return self.args[key]

    def __setitem__(self, key, val):
        self.args[key] = val

    def __len__(self):
        return len(self.args)

    def parse(self, key, default=None):
        arg = ''
        if key in self.data:
            if self.data[key] == '':
                if default == None:
                    error = 'Missing parameters {}'.format(key)
                    raise ValueError(error)
                else:
                    args = default
            elif not self.data[key] or self.data[key] == '':
                arg = default
            else:
                arg = self.data[key]
        else:
            if default == None:
                error = 'Missing parameters {}'.format(key)
                raise ValueError(error)
            else:
                arg = default
        self.args[key] = arg

# Customize base64
class Base64(object):

    def __init__(self, table='', padding='='):
        if table:
            self.table = table
        else:
            self.table = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'
        self.padding = padding

    def encode(self, msg):
        if isinstance(msg, bytes):
            data = msg
        else:
            data = str(msg).encode('utf8')
        bit = bitarray()
        bit.frombytes(data)
        fill = (6 - len(bit)%6)
        for i in range(fill): bit.append(0)
        code = ''
        for n in range(int(len(bit)/6)):
            b = ''
            for m in bit[6*n:6*(n+1)]:
                b += '1' if m else '0'
            code += self.table[int(b,2)]
        code += self.padding * (int(fill/2))
        if isinstance(msg, bytes):
            return code.encode('utf8')
        else:
            return code

    def decode(self, code):
        if isinstance(code, bytes):
            data = code
        else:
            data = str(code).encode('utf8')
        bitcode = ''
        for n in data.strip():
            c = chr(n)
            if c == self.padding:
                bitcode = bitcode[:-2]
            else:
                p = self.table.find(c)
                bitcode += '{0:06b}'.format(p)
        msg = bitarray(bitcode).tobytes()
        if isinstance(code, bytes):
            return msg
        else:
            return msg.decode('utf8')

class Thread(object):

    def __init__(self, func, MAX=10):
        self.lock = threading.Lock()
        self.func = func
        self.max = MAX
        self.num = 0

    def calc(self, sign):
        self.lock.acquire()
        if sign == '+':
            self.num += 1
        elif sign == '-':
            self.num -= 1
        self.lock.release()

    def thread(self, func, *argv):
        self.calc('+')
        try:
            func(*argv)
        except Exception:
            msg = traceback.format_exc()
            if logger:
                logger.info(msg)
            else:
                print(msg)
            
        self.calc('-')

    def run(self, *args):
        t = threading.Thread(target=self.thread, args=(self.func, *args))
        t.start()
        while self.num > self.max: time.sleep(1)

    def wait(self):
        while self.num > 0: time.sleep(1)

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

    os.chdir(sys.path[0])

    net = Netstat()
    json_print(net.filter(state='LISTEN'))

    #crypto = Crypto()
    #pwd = crypto.encode(msg).strip()
    #msg = crypto.decode(pwd)
    #print(pwd)
    #print(msg)
