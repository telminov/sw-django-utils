# coding: utf-8
import datetime
from djutils.date_utils import iso_to_datetime, iso_to_date, date_to_datetime, date_to_datetime_lte


def add_date_from_to_arguments(parser):
    parser.add_argument('--from',
                        dest='from',
                        help=u'начало выборки с дата/время изменения данных (например, 2011-07-22 12:45:00)', )
    parser.add_argument('--to',
                        dest='to',
                        help=u'конец выборки по дата/время изменения данных (например, 2011-07-22 20:00:00)', )
    parser.add_argument('--last_week',
                        dest='last_week',
                        help=u'обновить данные за последнюю неделю',
                        default=False,
                        action="store_true", )
    parser.add_argument('--last_day',
                        dest='last_day',
                        help=u'обновить данные за последний день',
                        default=False,
                        action="store_true", )
    parser.add_argument('--last_2hours',
                        dest='last_2hours',
                        help=u'обновить данные за последние 2 часа',
                        default=False,
                        action="store_true", )


def process_date_from_to_options(options, to_datetime=False, default_dt_to=False):
    """
        to_datetime - приводить ли date к datetime
        default_dt_to - устанавливать заведомо будущее дефолтное значение для dt_to
    """
    start_time = datetime.datetime.now()

    if options.get('last_week'):
        dt_from = start_time - datetime.timedelta(days=7)
        dt_to = start_time

    elif options.get('last_day'):
        dt_from = start_time - datetime.timedelta(days=1)
        dt_to = start_time

    elif options.get('last_2hours'):
        dt_from = start_time - datetime.timedelta(hours=2)
        dt_to = start_time

    else:
        from_str = options.get('from')
        if from_str:
            try:
                dt_from = iso_to_datetime(from_str)
            except:
                dt_from = iso_to_date(from_str)
        else:
            dt_from = None

        to_str = options.get('to')
        if to_str:
            try:
                dt_to = iso_to_datetime(to_str)
            except:
                dt_to = iso_to_date(to_str)
        else:
            dt_to = None

    if default_dt_to and not dt_to:
        dt_to = datetime.datetime(2100, 1, 1)

    if to_datetime:
        if isinstance(dt_from, datetime.date):
            dt_from = date_to_datetime(dt_from)
        if isinstance(dt_to, datetime.date):
            dt_to = date_to_datetime_lte(dt_to)

    return dt_from, dt_to
