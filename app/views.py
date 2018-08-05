#!/usr/bin/env python3

import os
import sys
import yaml
import json
import copy
import logging
import importlib
import traceback

from datetime import datetime

from app import app
from app.lib import tool
from app.lib import mysql

logger = tool.Log().stream_logger(__name__)

path = os.path.dirname(os.path.realpath(__file__))

date = datetime.now().strftime('[%Y-%m-%d %H:%M:%S] - ')
print(date,'Start Job App')

cur_job = ''
job_id = []

# Get Schedule
def get_schedule():
    try:
        with open('{}/app.yml'.format(path)) as y: setting = yaml.load(y)
        conf = setting['schedule']
        if conf['type'] == 'file':
            with open('{}/{}'.format(path, conf['path'])) as y: 
                schedule = yaml.load(y)
        elif conf['type'] == 'mysql':
            schedule = get_mysql_schedule(conf)
    except Exception as e:
        logger.error(traceback.format_exc())
        return
    return schedule

def get_mysql_schedule(conf):
    db = mysql.MySQL(conf['host'], conf['port'],
        conf['user'], conf['password'], conf['database'])
    sql = '''
        SELECT `class`,`script`,`kwargs`,`trigger`,
            `week`,`day`,`hour`,`minute`,`second`
        FROM `t_schedule` WHERE `app` = '{}' AND `enable` = 1
    '''.format(conf['app_name'])
    data = db.query(sql)
    schedule = {}
    for n in data:
        cls = n['class']
        if cls not in schedule: schedule[cls] = []
        task = {
            'name': n['script'],
            'setting': {
                'kwargs': json.loads(n['kwargs']),
                'trigger': n['trigger'],
            }
        }
        if n['trigger'] == 'interval':
            task['setting']['weeks'] = int(n['week'])
            task['setting']['days'] = int(n['day'])
            task['setting']['hours'] = int(n['hour'])
            task['setting']['minutes'] = int(n['minute'])
            task['setting']['seconds'] = int(n['second'])
        elif n['trigger'] == 'cron':
            task['setting']['week'] = n['week']
            task['setting']['day'] = n['day']
            task['setting']['hour'] = n['hour']
            task['setting']['minute'] = n['minute']
            task['setting']['second'] = n['second']
        schedule[cls].append(copy.deepcopy(task))
    db.close()
    return schedule

# Reload the module
def run_job(*args, **kwargs):
    attr = kwargs['__attr']
    del kwargs['__attr']
    importlib.reload(attr)
    mod = attr.Mod(logger)
    mod.run(*args, **kwargs)

# Add New Job
def add_job(new_job):
    global cur_job
    global job_id
    cur_job = new_job
    job_id = []
    for key, item in cur_job.items():
        for n in item:
            m = copy.deepcopy(n)
            try:
                attr = __import__('app.%s.%s'%(key, m['name']), fromlist=True)
                if 'kwargs' not in m['setting']: m['setting']['kwargs'] = {}
                m['setting']['kwargs']['__attr'] = attr
                job = app.add_job(run_job, **m['setting'], misfire_grace_time=60)
                job_id.append(job.id)
            except Exception:
                err = traceback.format_exc()
                logger.info(err)

# Check Schedule
def chk_job():
    global cur_job
    global job_id
    update = False
    new_job = get_schedule()
    if not new_job:
        logger.info('Get Schedule Error')
        sys.exit()
    if cur_job != new_job:
        if job_id: logger.info('Update Job!')
        for _id in job_id:
            app.remove_job(_id)
        add_job(new_job)

# Split the log file at 00:00
def reload():
    global logger
    imp.reload(tool)
    handler = logger.handlers[-1]
    if isinstance(handler, logging.FileHandler):
        for handler in logger.handlers:
            logger.removeHandler(handler)
        logger = tool.Log().file_logger(__name__)
        

app.add_job(reload, trigger='cron', hour=0, misfire_grace_time=60)
app.add_job(chk_job, trigger='interval', seconds=10, misfire_grace_time=60)
chk_job()
