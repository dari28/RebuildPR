"""Configuring the server at startup"""

import os
import sys
import traceback

from polyglot import load
from polyglot.downloader import Downloader
from polyglot.detect import Language
from background_task.models import Task

from lib import tools
from lib.mongo_connection import MongoConnection
from lib import stanford_module as stanford

def execution_at_startup():
    """Function that executes the necessary code at startup"""
    # polyglot_default_install()
    # standford_default_install()
    print("Server started")