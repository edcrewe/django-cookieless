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
CSRF protection without session Cookies to maintain a separate token from that passed via the URL or form posts.

However there are cases when it is required to use forms on a public site, where setting cookies is not desirable (due to privacy legislation), 
nor are complex rewritten URLs.

It is for that purpose this egg was devised.

To ameliorate the security implications, a whitelist of allowed domains or allowed URLs, can be set in the configuration. 

Usage can also be restricted to SSL only. 

As a final safety measure handling of GET requests can be turned off, so that the encrypted session id is not present in any URLs.

Please NOTE: It is not advisable to use this package without some form of the above restrictions being in place. 

The package also provides a decorator utility to turn off cookie setting for particular views (which also sets the csrf_exempt flag).

The package also handles the case of session handling for anonymous users with cookies disabled in the browser.

Installation
------------

To install add the package via pip or other build tool, e.g. bin/pip install django-cookieless

Then replace the standard Session in the middleware settings:

>>> MIDDLEWARE_CLASSES = (
...    'django.middleware.gzip.GZipMiddleware',
...    'django.middleware.common.CommonMiddleware',
...    'django.middleware.transaction.TransactionMiddleware',
...    # 'django.contrib.sessions.middleware.SessionMiddleware',
...    'cookieless.middleware.CookielessSessionMiddleware',
...)

The following two settings control its behaviour:

(see the example settings file)

Rewrite URLs to add session id for no_cookies decorated views 
(if False then all page navigation must be via form posts)

COOKIELESS['USE_GET'] = True

Rewriting the response automatically rather than use manual <% session_token %> <% session_url %> 

COOKIELESS['REWRITE'] = True

Use client ip and user agent to encrypt session key, to add some sort of CSRF protection given the standard CSRF has to be disabled without cookies.

COOKIELESS['CLIENT_ID'] = True

If this list is populated then only hosts that are specifically whitelisted are allowed to post to the server. So any domains that the site is served over should be added to the list. If no referer is found, the session is reset.
This helps protect against XSS attacks.

COOKIELESS['HOSTS'] = ['localhost', ]

Now you can decorate views to prevent them setting cookies, whilst still retaining the use of Sessions.
Usually this is easiest done in the urls.py of your core application ...

from cookieless.decorators import no_cookies

>>> urlpatterns = patterns('',
...    url(r'^view_function/(\d{1,6})$', no_cookies(view_function)),
...    url(r'^view_class/(\d{1,6})$', no_cookies(ViewClass.as_view())),
...)

COOKIELESS['NO_COOKIE_PERSIST'] = True

Further security option to not find and persist cookie based sessions as cookieless ones
since these may be tied to a user or other data. Instead new sessions are created for tying to cookieless data. 
This reduces the risk of cookieless allowing capture of a user's session - and hence privilege escalation attacks.


COOKIELESS['URL_SPECIFIC'] = True

Further security option to only keep a session for accessing a specific URL 

NOTE: If you turn on the django debug toolbar it will override, and set a session cookie, on the decorated views. So don't check to see if cookieless is working, with it enabled!

Tests
-----

The test suite sets up a simple application to test cookies manually, and to run the functional tests against.

Note that if the egg is installed normally, the cookieless.tests application will probably not have write permissions
so to run the tests install from src:

bin/pip install -e git+https://github.com/edcrewe/django-cookieless#egg=django-cookieless

Or move the tests application out and install separately as a django app.
Then run via:

bin/django-admin.py or manage.py test cookieless --settings="cookieless.tests.settings"

Note: Because the django test browser has some session implementation specific mocking, 
it fails to work if used directly against cookieless, so to stop it breaking other tests
cookieless checks to see if META['SERVER_NAME'] == 'testserver' and reverts to django.contrib.sessions if so.
