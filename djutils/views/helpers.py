# coding: utf-8
import re

from django.utils.http import urlquote
from django.utils.safestring import mark_safe

def url_path(request, base_url=None, is_full=False, *args, **kwargs):
    """
    join base_url and some GET-parameters to one; it could be absolute url optionally

    usage example:

        c['current_url'] = url_path(request, use_urllib=True, is_full=False)
        ...
        <a href="{{ current_url }}">Лабораторный номер</a>

    """
    if not base_url:
        base_url = request.path
        if is_full:
            protocol = 'https' if request.is_secure() else 'http'
            base_url = '%s://%s%s' % (protocol, request.get_host(), base_url)

    params = url_params(request, *args, **kwargs)
    url = '%s%s' % (base_url, params)
    return url

def url_params(request, except_params=None, as_is=False):
    """
    create string with GET-params of request

    usage example:
        c['sort_url'] = url_params(request, except_params=('sort',))
        ...
        <a href="{{ sort_url }}&sort=lab_number">Лабораторный номер</a>
    """
    if not request.GET:
        return ''
    params = []
    for key, value in request.GET.items():
        if except_params and key not in except_params:
            for v in request.GET.getlist(key):
                params.append('%s=%s' % (key, urlquote(v)))

    if as_is:
        str_params = '?' + '&'.join(params)
    else:
        str_params = '?' + '&'.join(params)
        str_params = urlquote(str_params)
    return mark_safe(str_params)


def prepare_sort_params(params, request, sort_key='sort', revers_sort=None, except_params=None):
    """
        Prepare sort params. Add revers '-' if need.
        Params:
            params - list of sort parameters
            request
            sort_key
            revers_sort - list or set with keys that need reverse default sort direction
            except_params - GET-params that will be ignored
        Example:
            view:
                c['sort_params'] = prepare_sort_params(
                    ('order__lab_number', 'order__client__lname', 'organization', 'city', 'street', ),
                    request,
                )
            template:
                   <th><a href="{{ sort_params.order__lab_number.url }}">Лабораторный номер</a></th>
               or
                    {% load djutils %}
                    ...
                    {% sort_th 'order__lab_number' 'Лабораторный номер' %}


    """
    current_param, current_reversed = sort_key_process(request, sort_key)

    except_params = except_params or []
    except_params.append(sort_key)

    base_url = url_params(request, except_params=except_params, as_is=True)

    sort_params = {}
    revers_sort = revers_sort or set()
    url_connector = '?' if request.get_full_path() == request.path else "&"
    for p in params:
        sort_params[p] = {}
        if current_param and p == current_param:
            prefix = '' if current_reversed else '-'
            sort_params[p]['url'] = base_url + "%s%s=%s" % (url_connector, sort_key, prefix + current_param)
            sort_params[p]['is_reversed'] = current_reversed
            sort_params[p]['is_current'] = True
        else:
            default_direction = '-' if p in revers_sort else ''
            sort_params[p]['url'] = base_url + "%s%s=%s%s" % (url_connector, sort_key, default_direction, p)
            sort_params[p]['is_reversed'] = False
            sort_params[p]['is_current'] = False

    return sort_params


def sort_key_process(request, sort_key='sort'):
    """
        process sort-parameter value (for example, "-name")
        return:
            current_param - field for sorting ("name)
            current_reversed - revers flag (True)
    """
    current = request.GET.get(sort_key)
    current_reversed = False
    current_param = None
    if current:
        mo = re.match(r'^(-?)(\w+)$', current)    # exclude first "-" (if exist)
        if mo:
            current_reversed = mo.group(1) == '-'
            current_param = mo.group(2)

    return current_param, current_reversed
