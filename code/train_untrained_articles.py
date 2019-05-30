import os
import sys
import django
_PATH = os.path.abspath(os.path.dirname(__file__))

if _PATH not in sys.path:
    sys.path.append(_PATH)

print(_PATH)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "newsAPI.settings")
django.setup()

import logging
logger = logging.getLogger()
logger.info('DJANGO START\n **************************')

from lib import learning_model as model
logger.info('train_untrained_article STARTED')
model.get_tags_from_untrained_articles()
logger.info('train_untrained_article FINISHED')
