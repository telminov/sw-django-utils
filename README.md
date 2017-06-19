# sw-django-utils
Soft Way company django utils
## Installation
1. Either checkout ``sw-django-utils`` from GitHub, or install using pip:
```bash
pip install sw-django-utils
```
2. Add ``sw-django-utils`` to your ``INSTALLED_APPS``:
```python
INSTALLED_APPS += (
    'djutils',
)
```
## Using Sorting
In view:
```python
class Search(SortMixin, ListView):
    model = models.ExampleModel
    template_name = 'ExampleSearch.html'
    sort_params = ['example_field', 'date_start', 'date_end']
```
In template:
```html
{% load djutils %}
<table>
    <tr>
        <th>#</th>
        {% sort_th 'example_field' 'Example' %}
        {% sort_th 'date_start' 'Created' %}
        {% sort_th 'date_end' 'Expiring date' %}
    </tr>
    ...
</table>    
```
