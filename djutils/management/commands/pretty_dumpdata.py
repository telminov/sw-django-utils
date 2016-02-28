# coding: utf-8
from io import StringIO
from django.core.management.commands.dumpdata import Command as Dumpdata


class Command(Dumpdata):
    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)

    def handle(self, *args, **kwargs):
        orig_stdout = self.stdout
        self.stdout = StringIO()
        super(Command, self).handle(*args, **kwargs)
        data = self.stdout.getvalue()

        data = data.encode("utf-8").decode("unicode_escape")

        orig_stdout.write(data)

        return data