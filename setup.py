# coding: utf-8
# python setup.py sdist register upload
from distutils.core import setup

setup(
    name='sw-django-utils',
    version='0.0.11',
    description='Soft Way company django utils.',
    author='Telminov Sergey',
    url='https://github.com/telminov/sw-django-utils',
    packages=[
        'djutils',
        'djutils.views',
        'djutils.tests',
        'djutils.templatetags',
    ],
    license='The MIT License',
    install_requires=[
        'django',
        'sqlparse==0.1.16',
    ],
)
