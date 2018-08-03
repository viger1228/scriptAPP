#!/usr/bin/env python3

import os
import sys
import yaml
import copy
import logging
import importlib
import traceback

from datetime import datetime

from app import app
from app.lib import tool

logger = tool.Log().stream_logger(__name__)

path = os.path.dirname(os.path.realpath(__file__))

date = datetime.now().strftime('[%Y-%m-%d %H:%M:%S] - ')
print(date,'Start Job App')

cur_job = ''
job_id = []

# Get Schedule
def get_schedule():
    with open('%s/schedule.yml'%(path)) as y: schedule = yaml.load(y)
    return schedule

# Reload the module
def run_job(*args, **kwargs):
    attr = kwargs['__attr']
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
                job = app.add_job(run_job, **m['setting'])
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
        logger.info('No Setting in schedule.yaml')
        return
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
        

app.add_job(reload, trigger='cron', hour=0)
app.add_job(chk_job, trigger='interval', seconds=10)
chk_job()
