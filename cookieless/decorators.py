# The django test client has mock session / cookies which assume cookies are in use
# so turn off cookieless for tests
# TODO: Find better work around for test browser switch hardcoded
#       to django.contrib.session being in MIDDLEWARE
from functools import wraps
from django.utils.decorators import available_attrs

# Just tags the view for special handling by the middleware
# but only do so if we aren't in testing mode ...
from django.conf import settings
import sys

if not hasattr(settings, "TESTING"):
    try:
        settings.TESTING = sys.argv[1:2] == ["test"]
    except:
        settings.TESTING = False


def no_cookies(view_func):
    """
    Marks a view function as not being allowed to set cookies
    Also sets same flag as django.views.decorators.csrf.csrf_exempt
    """

    def wrapped_view(*args, **kwargs):
        """We could just do view_func.csrf_exempt = True, but decorators
           are nicer if they don't have side-effects, so we return a new
           function.
        """
        if args:
            request = args[0]
        elif kwargs.has_key("request"):
            request = kwargs["request"]

        if not settings.TESTING:
            setattr(request, "no_cookies", True)

        return view_func(*args, **kwargs)

    if not settings.TESTING:
        # mark on intial decoration - rather than on running the view
        view_func.no_cookies = True
        view_func.csrf_exempt = True
    return wraps(view_func, assigned=available_attrs(view_func))(wrapped_view)
