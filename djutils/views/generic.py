# coding: utf-8
from django.shortcuts import redirect
from djutils.views.helpers import prepare_sort_params


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
        response = super().post(request, *args, **kwargs)
        self.logger.info(self.get_title(), extra={'POST': self.request.POST, 'username': self.request.user.username})
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

    def get_default_sort_param(self):
        return self.sort_params[0]

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

