# coding: utf-8
import json
from collections import OrderedDict

from django.forms import model_to_dict
from django.core.serializers.json import DjangoJSONEncoder


def object_to_json(obj, indent=2):
    """
        transform object to json
    """
    instance_json = json.dumps(obj, indent=indent, ensure_ascii=False, cls=DjangoJSONEncoder)
    return instance_json


def model_to_json(model_instance):
    """
        transform instance to json
    """
    instance_dict = model_to_dict(model_instance)
    return object_to_json(instance_dict)


def qs_to_json(qs, fields=None):
    """
    transform QuerySet to json
    """
    if not fields :
        fields = [f.name for f in qs.model._meta.fields]


    # сформируем список для сериализации
    objects = []
    for value_dict in qs.values(*fields):
        # сохраним порядок полей, как определено в моделе
        o = OrderedDict()
        for f in fields:
            o[f] = value_dict[f]
        objects.append(o)

    # сериализуем
    json_qs = json.dumps(objects, indent=2, ensure_ascii=False, cls=DjangoJSONEncoder)
    return json_qs


def mongoqs_to_json(qs, fields=None):
    """
    transform mongoengine.QuerySet to json
    """

    l = list(qs.as_pymongo())

    for element in l:
        element.pop('_cls')

    # use DjangoJSONEncoder for transform date data type to datetime
    json_qs = json.dumps(l, indent=2, ensure_ascii=False, cls=DjangoJSONEncoder)
    return json_qs


