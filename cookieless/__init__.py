# See http://peak.telecommunity.com/DevCenter/setuptools#namespace-packages
try:
    __import__('pkg_resources').declare_namespace(__name__)
except ImportError:
    from pkgutil import extend_path
    __path__ = extend_path(__path__, __name__)

from django.contrib.sessions.middleware import SessionMiddleware 
from cookieless.middleware import CookielessSessionMiddleware
# Monkey patch session middleware
SessionMiddleware = CookielessSessionMiddleware
