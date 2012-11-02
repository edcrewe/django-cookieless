from sys import stderr # make wsgi happy with print statements
from django.conf.urls.defaults import *

# URL patterns for django-cookieless
#from django.core.handlers.base import BaseHandler

urlpatterns = patterns('django-cookieless.views',
  # Add url patterns here
)

#try:
    # Monkey patch session middleware - 
    # Do it in urls since urls is only imported once, 
    # when the first request hits the server, after the apps are loaded.
#    from django.contrib.sessions.middleware import SessionMiddleware 
#    from cookieless.middleware import CookielessSessionMiddleware
#    SessionMiddleware = CookielessSessionMiddleware
#    SessionMiddleware.process_request = process_request # CookielessSessionMiddleware
#    SessionMiddleware.process_response = process_response
#    print >> stderr, 'Monkey patched contrib.sessions.middleware for django-cookieless'
#except:
#    print >> stderr, 'Failed to patch contrib.sessions.middleware for django-cookieless'


#base = BaseHandler()
#base.load_middleware()
#raise Exception(base._response_middleware)
