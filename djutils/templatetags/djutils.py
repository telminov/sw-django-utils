# coding: utf-8
from django import template
import sqlparse

register = template.Library()

@register.filter('pretty_sql')
def pretty_sql(sql):
    try:
        sql = sqlparse.format(sql, reindent=True, keyword_case='upper')
        return sql
    except Exception:
        return sql
