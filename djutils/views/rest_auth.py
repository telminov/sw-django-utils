# coding: utf-8
from django.http import HttpResponse, JsonResponse
from django.template import Template, RequestContext
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.forms import AuthenticationForm
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET
from djutils.forms import transform_form_error


@csrf_exempt
@require_POST
def login(request):
    form = AuthenticationForm(request, data=request.POST)
    if form.is_valid():
        auth_login(request, form.get_user())
        return JsonResponse({'login': 'ok'})
    else:
        errors = transform_form_error(form)
        c = {'errors': errors}
        return JsonResponse(c, status=403)

@csrf_exempt
@require_POST
def logout(request):
    auth_logout(request)
    return JsonResponse({'logout': 'ok'})


@require_GET
def get_current_user(request):
    c = {
        'is_authenticated': request.user.is_authenticated(),
    }
    if request.user.is_authenticated():
        c.update({
            'username': request.user.username,
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'email': request.user.email,
            'is_staff': request.user.is_staff,
            'is_active': request.user.is_active,
        })
    return JsonResponse(c)
