# coding: utf-8


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
