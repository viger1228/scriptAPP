#!/usr/bin/env python3

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.executors.pool import ThreadPoolExecutor
from app.lib import tool

executors = {
    'default': ThreadPoolExecutor(100)
}

app = BlockingScheduler(executors=executors)

from app import views
