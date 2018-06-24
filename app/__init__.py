#!/usr/bin/env python3

from apscheduler.schedulers.blocking import BlockingScheduler
from app.lib import tool

app = BlockingScheduler()

from app import views
