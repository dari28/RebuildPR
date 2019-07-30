import logging
import json
from django.utils.deprecation import MiddlewareMixin
from django.http.response import JsonResponse

from lib.json_encoder import JSONEncoderHttp


class ResponseMiddleware(MiddlewareMixin):

    def process_response(self, request, response):
        logger = logging.getLogger('ResponseMiddlewareLogger')

        # if not json.loads(response.content)['status']:
        #     logger.error(response.content)
        try:
            resp = json.loads(response.content)
        except ValueError:
            resp = response._headers
        if 'status' in resp and not resp['status']:
            return response
        else:
            results = {'status': True, 'response': resp, 'error': {}}
            final_response = JsonResponse(results, encoder=JSONEncoderHttp)
            end_log_string = 'Stop {} '.format(request.path.replace('/', ''))
            if request.POST:
                end_log_string += 'Request: {}'.format(json.dumps(request.POST.decode("utf-8")))
            else:
                end_log_string += 'Request: {}'.format(json.dumps(request.body.decode("utf-8")))
            if request.FILES:
                end_log_string += ' Files: '
                for key in request.FILES.keys():
                    file = request.FILES[key]
                    end_log_string += 'name: {}, type: {}, size: {} bytes '.format(
                        file._name,
                        file.content_type,
                        file._size
                    )
            if request.META and 'REMOTE_ADDR' in request.META:
                end_log_string += 'REMOTE_ADDR: {}'.format(request.META['REMOTE_ADDR'])
        end_log_string += 'Result: {}'.format(results)
        logger.info(end_log_string)
        return final_response