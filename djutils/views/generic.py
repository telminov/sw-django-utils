# coding: utf-8
import six

from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import ImproperlyConfigured, PermissionDenied
from django.shortcuts import redirect
from django.utils.encoding import force_text

from djutils.views.helpers import prepare_sort_params
from django.http import QueryDict
from django.views.generic.edit import FormMixin as DjangoFormMixin

# last django , django 1.8
try:
    from urllib.parse import quote
    from django.urls import reverse
    from django.contrib.auth.mixins import PermissionRequiredMixin as PermissionRequiredMixinAuth

except ImportError:
    from urllib import quote
    from django.core.urlresolvers import reverse

    class PermissionRequiredMixinAuth(object):
        login_url = None
        permission_denied_message = ''
        raise_exception = False
        permission_required = None
        redirect_field_name = REDIRECT_FIELD_NAME

        def get_login_url(self):
            login_url = self.login_url or settings.LOGIN_URL
            if not login_url:
                raise ImproperlyConfigured(
                    '{0} is missing the login_url attribute. Define {0}.login_url, settings.LOGIN_URL, or override '
                    '{0}.get_login_url().'.format(self.__class__.__name__)
                )
            return force_text(login_url)

        def get_permission_denied_message(self):
            return self.permission_denied_message

        def get_redirect_field_name(self):
            return self.redirect_field_name

        def handle_no_permission(self):
            if self.raise_exception:
                raise PermissionDenied(self.get_permission_denied_message())
            return redirect_to_login(self.request.get_full_path(), self.get_login_url(), self.get_redirect_field_name())

        def get_permission_required(self):
            if self.permission_required is None:
                raise ImproperlyConfigured(
                    '{0} is missing the permission_required attribute. Define {0}.permission_required, or override '
                    '{0}.get_permission_required().'.format(self.__class__.__name__)
                )
            if isinstance(self.permission_required, six.string_types):
                perms = (self.permission_required,)
            else:
                perms = self.permission_required
            return perms

        def has_permission(self):
            perms = self.get_permission_required()
            return self.request.user.has_perms(perms)

        def dispatch(self, request, *args, **kwargs):
            if not self.has_permission():
                return self.handle_no_permission()
            return super(PermissionRequiredMixin, self).dispatch(request, *args, **kwargs)


class TitleMixin(object):
    title = ''

    def get_title(self):
        return self.title

    def get_context_data(self, **kwargs):
        c = super(TitleMixin, self).get_context_data(**kwargs)

        title = self.get_title()
        if title:
            c['title'] = title

        return c


class LoggerMixin(object):
    logger = None

    def get(self, request, *args, **kwargs):
        response = super(self, LoggerMixin).get(request, *args, **kwargs)
        self.logger.debug(self.get_title(), extra={'GET': request.GET, 'username': request.user.username})
        return response

    def post(self, request, *args, **kwargs):
        title = self.get_title()
        response = super(self, LoggerMixin).post(request, *args, **kwargs)
        self.logger.info(title, extra={'POST': self.request.POST, 'username': self.request.user.username})
        return response


class SortMixin(object):
    sort_params = None          # must be defined
    sort_param_name = 'sort'
    sort_qs = True

    def get_queryset(self):
        qs = super(self, SortMixin).get_queryset()
        if self.sort_qs:
            order_by = self.request.GET[self.sort_param_name]
            qs = qs.order_by(order_by)
        return qs

    def get(self, request, *args, **kwargs):
        if not request.GET.get(self.sort_param_name):
            redirect_url = request.get_full_path()
            if not request.GET:
                redirect_url += '?'
            else:
                redirect_url += '&'
            redirect_url += self.sort_param_name + '=' + self.get_default_sort_param()
            return redirect(redirect_url)

        response = super(self, SortMixin).get(request, *args, **kwargs)
        return response

    @classmethod
    def get_default_sort_param(cls):
        return cls.sort_params[0]

    def get_sort_except_params(self):
        except_params = []
        if hasattr(self, 'page_kwarg') and self.page_kwarg:
            except_params.append(self.page_kwarg)
        return except_params

    def get_context_data(self, **kwargs):
        c = super(self, SortMixin).get_context_data(**kwargs)
        c['sort_params'] = prepare_sort_params(
            self.sort_params,
            request=self.request,
            sort_key=self.sort_param_name,
            except_params=self.get_sort_except_params()
        )
        return c


class FilterMixin(object):
    filter = None

    def get_queryset(self):
        qs = super(self, FilterMixin).get_queryset()
        self.filter_obj = self.filter(self.request.GET, qs)
        return self.filter_obj.qs

    def get_context_data(self, **kwargs):
        c = super(self, FilterMixin).get_context_data(**kwargs)
        c['form'] = self.filter_obj.form
        return c


class PageMixin:
    def get_context_data(self, **kwargs):
        c = super(self, PageMixin).get_context_data(**kwargs)
        if c.get('page_obj'):
            c['start_counter'] = (c['page_obj'].number - 1) * c['page_obj'].paginator.per_page
        return c


class BreadcrumbsMixin(object):
    def get_breadcrumbs(self):
        return []

    def get_context_data(self, **kwargs):
        kwargs['breadcrumbs'] = self.get_breadcrumbs()
        return super(self, BreadcrumbsMixin).get_context_data(**kwargs)


class FormMixin(DjangoFormMixin):
    request_method = 'post'

    def form_process(self):
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def get(self, *args, **kwargs):
        if self.request_method == 'get':
            return self.form_process()

        return super(self, FormMixin).get(*args, **kwargs)

    def post(self, *args, **kwargs):
        if self.request_method == 'post':
            return self.form_process()

        return super(self, FormMixin).post(*args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(self, FormMixin).get_form_kwargs()
        kwargs['data'] = getattr(self.request, self.request_method.upper(), None) or None
        return kwargs


class NextMixin(object):
    def get_next(self):
        return self.request.GET.get('next')

    def get_context_data(self, **kwargs):
        kwargs['next'] = self.get_next()
        return super(self, NextMixin).get_context_data(**kwargs)


class PermissionRequiredMixin(PermissionRequiredMixinAuth):
    def handle_no_permission(self):
        url = reverse('permission_denied')
        params = QueryDict(mutable=True)
        params['url'] = self.request.path

        previous_url = self.request.META.get('HTTP_REFERER')
        if previous_url:
            params['next'] = quote(previous_url)
        url += '?%s' % params.urlencode()

        return redirect(url)