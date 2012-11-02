from functools import wraps
from django.utils.decorators import available_attrs
# Just tags the view for special handling by the middleware

def no_cookies(view_func):
    """
    Marks a view function as not being allowed to set cookies
    Also sets same flag as django.views.decorators.csrf.csrf_exempt
    """
    def wrapped_view(*args, **kwargs):
        '''We could just do view_func.csrf_exempt = True, but decorators
           are nicer if they don't have side-effects, so we return a new
           function.
        '''   
        #Assumes request is args[0]
        if args:
            setattr(args[0], 'no_cookies', True)
        elif kwargs.has_key('request'):
            setattr(kwargs['request'], 'no_cookies', True)
        return view_func(*args, **kwargs)

    wrapped_view.csrf_exempt = True
    wrapped_view.no_cookies = True
    return wraps(view_func, assigned=available_attrs(view_func))(wrapped_view)
