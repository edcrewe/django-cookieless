Django Cookieless
=================

Ed Crewe - November 2012

Overview
--------

This package provides a sessions implementation and decorator class for views to
allow for forms to maintain state without using cookies by posting the session
id between forms, or via urls.

Django requires cookies to maintain session, and hence for authorisation.

This package is designed to cater for anonymous user session maintenance, without cookies.

WARNING : There are security issues with this, since it is not possible to use
CSRF protection without either URL rewriting or Cookies to maintain a separate 
token from that posted in the form.

However there are cases when it is required to use forms on a public site, where
setting cookies is not desirable (due to privacy legislation), 
nor are complex rewritten URLs.

It is for that purpose this egg was devised.

To ameliorate the security implications, a whitelist of allowed domains or allowed URLs, can be set in the configuration. 
Usage can also be restricted to SSL only. 
As a final safety measure handling of GET requests can be turned off.

Please NOTE: It is not advisable to use this package without some form of the above restrictions being in place. 

The package also provides a decorator utility to turn off cookie setting for particular views (which also sets the csrf_exempt flag).

The package also handles the case of session handling for users with cookies disabled in the browser.

Installation
------------

To install add the package via pip or other build tool, e.g. bin/pip install django-cookieless

Then replace the standard Session in the middleware settings ...

MIDDLEWARE_CLASSES = (
    'django.middleware.gzip.GZipMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.transaction.TransactionMiddleware',
    # 'django.contrib.sessions.middleware.SessionMiddleware',
    'cookieless.middleware.CookielessSessionMiddleware',
)

The following two settings control its behaviour ...

Rewrite URLs to add session id for no_cookies decorated views 
(if False then all page navigation must be via form posts)

COOKIELESS_USE_GET = True

Rewriting the response automatically rather than use manual <% session_token %> <% session_url %> 

COOKIELESS_REWRITE = True

Now you can decorate views to prevent them setting cookies, whilst still retaining the use of Sessions
Usually this is easiest done in the urls.py of your core application ...

from cookieless.decorators import no_cookies

urlpatterns = patterns('',
    url(r'^view_function/(\d{1,6})$', no_cookies(view_function)),
    url(r'^view_class/(\d{1,6})$', no_cookies(ViewClass.as_view())),
)




