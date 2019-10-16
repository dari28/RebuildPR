import re

from pymongo.errors import WriteError

from lib.mongo_connection import MongoConnection
from lib.tools import punctuation, trim_punkt, get_dir_path
from nlp.config import UNITS_PATH


def install():
    mongo = MongoConnection()
    mongo.units.remove({})
    with open(UNITS_PATH, 'r') as f:
        for line in f:
            if line.strip():
                if line.startswith('#'):
                    continue
                split = line.split(',')
                split = [s.strip().lower() for s in split if s.strip() != '']
                mongo.units.insert_one({'unit': split[0], 'variations': split})


if __name__ == '__main__':
    install()
