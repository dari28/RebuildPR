import logging
import json
from django.utils.deprecation import MiddlewareMixin
from django.http.response import JsonResponse

from lib.tools import get_error
from lib.json_encoder import JSONEncoderHttp


class LoggingMiddleware(MiddlewareMixin):

    def process_view(self, request, view_func, view_args, view_kwargs):
        self.module_name = view_func.__module__
        self.func_name = view_func.__name__
        logger = logging.getLogger(view_func.__module__)
        logger.info('Start {}'.format(view_func.__name__))
        speech_func = ['speech_to_text', 'speech_to_text_stream']
        if not view_func.__name__ in speech_func:

            if request.POST:

                logger.debug('"Params": {}'.format(json.dumps(request.POST)))
            else:
                nr = request.body.decode("utf-8") if isinstance(request.body, bytes) else request.body
                logger.debug('"Params": {}'.format(json.dumps(nr)))

    def process_response(self, request, response):
        logger = logging.getLogger(self.module_name)

        # if not json.loads(response.content)['status']:
        #     logger.error(response.content)

        logger.info('Stop {}'.format(self.func_name))
        return response

    def process_exception(self, request, exception):
        logger = logging.getLogger(self.module_name)
        results = {
            'status': False,
            'response': {},
            'error': get_error()
        }
        logger.error(json.dumps(results))
        return JsonResponse(results, encoder=JSONEncoderHttp)
