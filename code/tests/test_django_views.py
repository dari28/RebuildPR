import unittest
import os
import traceback
import sys

sys.path.insert(0,'/home/user/projects/python_pr_relations_nlp/code')
#print(sys.path)
os.environ["JAVA_HOME"] = "/usr/lib/jvm/java-1.8.0-openjdk-amd64"

os.environ.setdefault("DJANGO_SETTINGS_MODULE",'newsAPI.settings')

os.environ.get("DJANGO_SETTINGS_MODULE")

from copy import deepcopy
from json import loads
from django import setup
setup()

from django.test import LiveServerTestCase, RequestFactory
from django.http.response import JsonResponse

from tests.utils_4test import convert_doc
from nlp import urls


class DjangoApiTests(LiveServerTestCase):


   request_factory = RequestFactory()

   EXPECTED_RETURN_TYPE = {'status': bool,
                           'response': dict,
                           'error': dict}

   ERROR_STRUCTURE = {"MessageError": str,
                      "TypeError": str,
                      "TracebackError": str}

   def check_api(self, api_method):
        '''
        Method for automatization of django views testing
        :param api_method: any function or method with correct __doc__ attribute
        :return: None
        '''
        def response_check(api_method, request, tested_argv=None):
            try:
                #TODO methods must content default 'option' and expected one method post or get, using few methods unsupported
                methods = api_method.view_class.http_method_names
                request_factory = {'get': self.request_factory.get,
                                   'post': self.request_factory.post}
                print(request)
                if 'get' in methods:
                    test_request = request_factory['get'](path='test', data=request)
                elif 'post' in methods:
                    test_request = request_factory['post'](path='test', data=request)

                response = api_method(test_request)
            except:

                trace = traceback.format_exc()
                print("Exception occured:\n{}\n\n".format(trace))
                raise AssertionError(
                    '\napi_function:{0} \nexectution error with arguments {1}'.format(api_method.__name__, request))
            else:

                with self.subTest('Check response type'):
                    self.assertIsInstance(response, JsonResponse,
                                          'response is not a django JsonResponse')
                try:
                    response_dict =loads(response.content)
                    print(response_dict)
                except:
                    trace = traceback.format_exc()
                    print("Exception occured:\n{}\n\n".format(trace))
                    raise AssertionError()
                else:

                    for expected_key in self.EXPECTED_RETURN_TYPE:
                        with self.subTest(Check_key=expected_key):

                            self.assertIn(expected_key, response_dict,
                                          'Response have not got {0} as key'.format(expected_key))

                            self.assertIsInstance(response_dict[expected_key],
                                                  self.EXPECTED_RETURN_TYPE[
                                                      expected_key],
                                                  'Unexpected response {0} type'.format(expected_key))

                    if response_dict['status']:

                        self.assertDictEqual(response_dict['error'], {},
                                             'error  is not empty with status true: {0}'.format(response_dict['error']))
                    else:

                        self.assertNotEqual(response_dict['error'], {},
                                            'error is empty with status false')

                        for expected_key in self.ERROR_STRUCTURE:
                            with self.subTest(check_key=expected_key):
                                self.assertIn(expected_key,
                                              response_dict['error'],
                                              'Incorrect response')

                                self.assertIsInstance(
                                    response_dict['error'][expected_key],
                                    self.ERROR_STRUCTURE[
                                        expected_key],
                                    'Unexpected type response error:{0}{1}'.format(expected_key,
                                                                                    response_dict["error"][expected_key]))

                        self.assertEqual(response_dict['error']["MessageError"],
                                         "Missing mandatory parameter \'<'{0}'>\'".format(tested_argv),
                                         'Unexpected MessageError')

        #with self.subTest('Check  function/method __doc__ attribute not empty'):
        self.assertIsNotNone(api_method.__doc__,
                     '\n\nFor using this test, must be filled __doc__'
                     ' attribute of function/method as example:\n'
                     'def some_function(a,b):\n'
                     '"""\n'
                     ' :param request: { "name":"SomeName"} \n'
                     ':return: \n'
                     ':required: {"data":{"name":1}} \n'
                     '"""')

        __data, _, __require = convert_doc(api_method)

        sub_tests_request=[['full_request', __data['request']]]
        if __require is not None:
            for require in __require:
                if __require[require]:
                    tmp = deepcopy(__data['request'])
                    _ = tmp.pop(require)
                    sub_tests_request.append([require, tmp])

        for name, data in sub_tests_request:

            if name == 'full_request':
                response_check(api_method, data)
            else:
                response_check(api_method, data, name)


   def test_vievs_from_urls(self):

        from unittest.mock import patch
        import mongomock
        with patch('pymongo.MongoClient', mongomock.MongoClient):
            for function_with_url in urls.urlpatterns:

                function = function_with_url.callback
                name = function_with_url.callback.__name__

                with self.subTest(name):
                     self.check_api(function)


if __name__ == '__main__':

    DjangoViewsTestSuite = unittest.TestSuite()
    DjangoViewsTestSuite.addTest(unittest.makeSuite(DjangoApiTests))
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(DjangoViewsTestSuite)







