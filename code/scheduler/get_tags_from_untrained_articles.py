import os
import sys
import django
_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

if _PATH not in sys.path:
    sys.path.append(_PATH)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "newsAPI.settings")

# export POLYGLOT_DATA_PATH=/var/local
POLYGLOT_DATA_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
os.environ.setdefault("POLYGLOT_DATA_PATH", POLYGLOT_DATA_PATH)

import logging
logger = logging.getLogger()
logger.info(_PATH)

django.setup()

logger.info('DJANGO START\n **************************')

from lib import learning_model as model
logger.info('get_tags_from_untrained_articles STARTED')
model.get_tags_from_untrained_articles()
logger.info('get_tags_from_untrained_articles FINISHED')


