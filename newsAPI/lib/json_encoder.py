import json
from datetime import datetime
import numpy

from bson import ObjectId
from rest_framework.renderers import JSONRenderer
from rest_framework.utils import encoders
from django.core.serializers.json import DjangoJSONEncoder


class JSONEncoder(json.JSONEncoder):
    """JSONEncoder for import/export model"""
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        if isinstance(o, datetime):
            return str(o)
        if isinstance(o, numpy.integer):
            return int(o)
        return json.JSONEncoder.default(self, o)


class JSONEncoderHttp(DjangoJSONEncoder):
    """JSONEncoder for custom JSONRender """
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        if isinstance(o, numpy.integer):
            return int(o)
        return super(JSONEncoderHttp, self).default(o)


class JSONEncoderRender(encoders.JSONEncoder):
    """JSONEncoder for custom JSONRender """
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        if isinstance(o, numpy.integer):
            return int(o)
        return encoders.JSONEncoder.default(self, o)


class JSONRender(JSONRenderer):
    """JSONRender for response views"""
    encoder_class = JSONEncoderRender
