# coding: utf-8
import re
from urllib.parse import quote
from django import http
from django.conf import settings
from django.http import HttpResponseRedirect

XS_SHARING_ALLOWED_ORIGINS = getattr(settings, 'XS_SHARING_ALLOWED_ORIGINS', '*')
XS_SHARING_ALLOWED_METHODS = getattr(settings, 'XS_SHARING_ALLOWED_METHODS', ['POST', 'GET', 'OPTIONS', 'PUT', 'DELETE'])
XS_SHARING_ALLOWED_HEADERS = getattr(settings, 'XS_SHARING_ALLOWED_HEADERS', ['Content-Type', '*'])
XS_SHARING_ALLOWED_CREDENTIALS = getattr(settings, 'XS_SHARING_ALLOWED_CREDENTIALS', 'true')


class XsSharing(object):
    """
    This middleware allows cross-domain XHR using the html5 postMessage API.

    Access-Control-Allow-Origin: http://foo.example
    Access-Control-Allow-Methods: POST, GET, OPTIONS, PUT, DELETE

    Based off https://gist.github.com/426829
    """
    def process_request(self, request):
        if 'HTTP_ACCESS_CONTROL_REQUEST_METHOD' in request.META:
            response = http.HttpResponse()
            if settings.DEBUG and 'HTTP_ORIGIN' in request.META:
                response['Access-Control-Allow-Origin'] = request.META['HTTP_ORIGIN']
            else:
                response['Access-Control-Allow-Origin'] = XS_SHARING_ALLOWED_ORIGINS
            response['Access-Control-Allow-Methods'] = ",".join( XS_SHARING_ALLOWED_METHODS )
            response['Access-Control-Allow-Headers'] = ",".join( XS_SHARING_ALLOWED_HEADERS )
            response['Access-Control-Allow-Credentials'] = XS_SHARING_ALLOWED_CREDENTIALS
            return response

        return None

    def process_response(self, request, response):
        if settings.DEBUG and 'HTTP_ORIGIN' in request.META:
            response['Access-Control-Allow-Origin'] = request.META['HTTP_ORIGIN']
        else:
            response['Access-Control-Allow-Origin'] = XS_SHARING_ALLOWED_ORIGINS
        response['Access-Control-Allow-Methods'] = ",".join( XS_SHARING_ALLOWED_METHODS )
        response['Access-Control-Allow-Headers'] = ",".join( XS_SHARING_ALLOWED_HEADERS )
        response['Access-Control-Allow-Credentials'] = XS_SHARING_ALLOWED_CREDENTIALS

        return response


EXEMPT_URLS = [
    re.compile(getattr(settings, 'LOGIN_URL', '/login/')),
    re.compile(getattr(settings, 'LOGOUT_URL', '/logout/')),
]
if hasattr(settings, 'LOGIN_EXEMPT_URLS'):
    EXEMPT_URLS += [re.compile(expr) for expr in settings.LOGIN_EXEMPT_URLS]

class LoginRequired(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.user.is_authenticated():
            path = request.path_info
            if not any(m.match(path) for m in EXEMPT_URLS):
                next = '?next=%s' % quote(path)
                url = settings.LOGIN_URL + next
                return HttpResponseRedirect(url)
        response = self.get_response(request)
        return response