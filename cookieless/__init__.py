# See http://peak.telecommunity.com/DevCenter/setuptools#namespace-packages
from django.contrib.admin import checks


try:
    __import__("pkg_resources").declare_namespace(__name__)
except ImportError:
    from pkgutil import extend_path

    __path__ = extend_path(__path__, __name__)


def cookieless_contains_class(class_path, candidate_paths):
    """
    Return whether or not a dotted class path is
    found in a list of candidate paths.
    Disable blocking use of admin with cookieless.
    """
    if (
        class_path == "django.contrib.sessions.middleware.SessionMiddleware"
        or class_path in candidate_paths
    ):
        return True


checks._contains_subclass = cookieless_contains_class
