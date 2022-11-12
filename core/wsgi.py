"""
WSGI config for core project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/howto/deployment/wsgi/
"""

import os

import socketio
from django.core.wsgi import get_wsgi_application
from sara.views import sio
from socketio import Middleware
import eventlet
import eventlet.wsgi
django_app = get_wsgi_application()
application = Middleware(sio, django_app)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')


eventlet.wsgi.server(eventlet.listen(('', 8000)), application)
