# coding: utf-8
import time
import socket
from django.conf import settings


def push(metric, value, timestamp=None, server=None, port=None):
    if not timestamp:
        timestamp = int(time.time())
    if not server:
        server = settings.GRAPHITE_HOST
    if not port:
        port = settings.GRAPHITE_PORT

    sock = socket.socket()
    sock.connect((server, int(port)))
    message = '%s %s %d\n' % (metric, value, timestamp)
    sock.sendall(message)
    sock.close()
