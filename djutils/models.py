# coding: utf-8
import six
from django.db import models
from django.conf import settings
from swutils.encrypt import decrypt, encrypt


class OneValueModel(models.Model):
    """
        Base model for key-value data storing.
        Example - system statues, counters and other.
    """
    NAME_CHOICES = None     # Available keys. Must be defined at sub class

    name = models.CharField(max_length=100, unique=True, choices=NAME_CHOICES)
    value = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        abstract = True

    @classmethod
    def get_value(cls, name, default=None, decrypt_it=False):
        instance, created = cls.objects.get_or_create(name=name, defaults={'value': default})
        value = instance.value

        if decrypt_it:
            value = decrypt(value, key=cls._get_key())

        return value

    @classmethod
    def set_value(cls, name, value, encrypt_it=False):
        if encrypt_it:
            value = encrypt(value, key=cls._get_key())

        cls.objects.get_or_create(name=name)    # create if needed
        return cls.objects.filter(name=name).update(value=value)

    @classmethod
    def _get_key(cls):
        key = settings.SECRET_KEY
        if isinstance(key, six.text_type):
            key = key.encode()
        return key