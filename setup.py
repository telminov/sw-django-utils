# coding: utf-8
from distutils.core import setup

setup(
    name='sw-django-utils',
    version='0.0.3',
    description='Soft Way company django utils.',
    author='Telminov Sergey',
    url='https://github.com/telminov/sw-django-utils',
    packages=['djutils',],
    license='The MIT License',
    install_requires=[
        'django',
    ],
)
