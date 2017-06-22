# coding: utf-8
from django import forms
from django.utils.safestring import mark_safe


class NameInput(forms.TextInput):
    media = forms.Media(js=(['djutils/js/capitalize.js']))

    def render(self, name, *args, **kwargs):
        return super(NameInput, self).render(name, *args, **kwargs) + mark_safe(
            '''
                <script type="text/javascript">
                    capitalize('input[type=text][name={}]');
                </script>
            '''.format(name)
        )

