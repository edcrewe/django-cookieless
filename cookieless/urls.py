from sys import stderr # make wsgi happy with print statements
from django.conf.urls.defaults import *

# URL patterns for django-cookieless

urlpatterns = patterns('django-cookieless.views',
  # Add url patterns here
)

try:
    # Monkey patch session middleware - 
    # Do it in urls since urls is only imported once, 
    # when the first request hits the server, after the apps are loaded.
    from django.contrib.sessions.middleware import SessionMiddleware 
    from cookieless.middleware import CookielessSessionMiddleware
    SessionMiddleware = CookielessSessionMiddleware
    print >> stderr, 'Monkey patched contrib.sessions.middleware for django-cookieless'
except:
    print >> stderr, 'Failed to patch contrib.sessions.middleware for django-cookieless'
