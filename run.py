#!/usr/bin/env python3

import os
import sys
import traceback

from app import app
from app import views
from app.lib import tool

if __name__ == '__main__':

    for handler in views.logger.handlers:
        views.logger.removeHandler(handler)

    if len(sys.argv) == 1:
        views.logger = tool.Log().stream_logger('app')
    else:
        views.logger = tool.Log().file_logger('app')

    try:
        app.start()
    except KeyboardInterrupt:
        pass
    except Exception:
        err = traceback.format_exc()
        views.logger(err)
