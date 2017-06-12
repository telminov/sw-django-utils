# coding: utf-8
from urllib.parse import quote

from django.shortcuts import redirect
from djutils.views.helpers import prepare_sort_params
from django.http import QueryDict
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic.edit import FormMixin as DjangoFormMixin
from django.contrib.auth.mixins import PermissionRequiredMixin as PermissionRequiredMixinAuth


class TitleMixin:
    title = ''

    def get_title(self):
        return self.title

    def get_context_data(self, **kwargs):
        c = super(TitleMixin, self).get_context_data(**kwargs)

        title = self.get_title()
        if title:
            c['title'] = title

        return c


class LoggerMixin:
    logger = None

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        self.logger.debug(self.get_title(), extra={'GET': request.GET, 'username': request.user.username})
        return response

    def post(self, request, *args, **kwargs):
        title = self.get_title()
        response = super().post(request, *args, **kwargs)
        self.logger.info(title, extra={'POST': self.request.POST, 'username': self.request.user.username})
        return response


class SortMixin:
    sort_params = None          # must be defined
    sort_param_name = 'sort'
    sort_qs = True

    def get_queryset(self):
        qs = super().get_queryset()
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

        response = super().get(request, *args, **kwargs)
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
        c = super().get_context_data(**kwargs)
        c['sort_params'] = prepare_sort_params(
            self.sort_params,
            request=self.request,
            sort_key=self.sort_param_name,
            except_params=self.get_sort_except_params()
        )
        return c


class FilterMixin:
    filter = None

    def get_queryset(self):
        qs = super().get_queryset()
        self.filter_obj = self.filter(self.request.GET, qs)
        return self.filter_obj.qs

    def get_context_data(self, **kwargs):
        c = super().get_context_data(**kwargs)
        c['form'] = self.filter_obj.form
        return c


class PageMixin:
    def get_context_data(self, **kwargs):
        c = super().get_context_data(**kwargs)
        if c.get('page_obj'):
            c['start_counter'] = (c['page_obj'].number - 1) * c['page_obj'].paginator.per_page
        return c


class BreadcrumbsMixin:
    def get_breadcrumbs(self):
        return []

    def get_context_data(self, **kwargs):
        kwargs['breadcrumbs'] = self.get_breadcrumbs()
        return super().get_context_data(**kwargs)


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

        return super().get(*args, **kwargs)

    def post(self, *args, **kwargs):
        if self.request_method == 'post':
            return self.form_process()

        return super().post(*args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['data'] = getattr(self.request, self.request_method.upper(), None) or None
        return kwargs


class NextMixin:
    def get_next(self):
        return self.request.GET.get('next')

    def get_context_data(self, **kwargs):
        kwargs['next'] = self.get_next()
        return super().get_context_data(**kwargs)


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