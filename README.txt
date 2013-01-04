Django Cookieless
=================

Ed Crewe - January 2013

Overview
--------

This package provides a sessions implementation and decorator class for views to
allow for forms to maintain state without using cookies by posting the session
id between forms, or via urls.

Django requires cookies to maintain session, and hence for authorisation.

This package is designed to cater for anonymous user session maintenance, without cookies.

WARNING : There are security issues with this, since it is not possible to use
CSRF protection without session Cookies to maintain a separate token from that passed via the URL or form posts.

However there are cases when forms are used on a public site, where setting cookies is not desirable (`due to privacy legislation <http://www.ico.gov.uk/>`_), since technically they are not required for anonymous users to respond to forms. 
So if used, may necessitate requesting permission to set cookies, from the user.

Hence this package was devised to allow django to deliver multipage forms, without using cookies.

To ameliorate the security implications, a whitelist of allowed domains, can be set in the configuration. 

Usage can also be restricted to a particular URL. 

As another safety measure, handling of GET requests can be turned off, so that the encrypted session id is not present in any URLs.

Please NOTE: It is not advisable to use this package without some form of the above restrictions being in place. 

For the purposes of using both cookie based and cookieless sessions together, there is a
custom cookieless_signal(sender=request, created) and a 'no_cookies' flag when cookieless sessions are saved.

Both cater for hooking up custom code for handling these less secure sessions. 

The package provides a decorator utility to turn off cookie setting for particular views (which also sets the csrf_exempt flag).

The package also handles the case of session handling for anonymous users with cookies disabled in the browser.

You can decorate views to prevent them setting cookies, whilst still retaining the use of Sessions.
Usually this is easiest done in the urls.py of your core application ...

from cookieless.decorators import no_cookies

>>> urlpatterns = patterns('',
...    url(r'^view_function/(\d{1,6})$', no_cookies(view_function)),
...    url(r'^view_class/(\d{1,6})$', no_cookies(ViewClass.as_view())),
...)

Note that if a number of browser tabs are open on to a site with cookieless, they will each maintain a completely separate session, since
without cookies the session is tied to the session posted from the pages accessed, not the client as a whole.

In cases where this is not the desired behaviour, then it can be reduced by using URL rewriting to make any links to open other windows pass session across. 
However of course this also means that potentially a session can be shared across browsers, too.

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

The following settings control its behaviour:

(see the example settings file)

1. Rewriting the response automatically rather than use manual <% session_token %> <% session_url %> 

COOKIELESS['REWRITE'] = True

2. Rewrite URLs to add session id for no_cookies decorated views (if False then all page navigation must be via form posts)

COOKIELESS['USE_GET'] = True

3. Use client ip and user agent to encrypt session key, to add some sort of CSRF protection given the standard CSRF has to be disabled without cookies.

COOKIELESS['CLIENT_ID'] = True

4. If this list is populated then only hosts that are specifically whitelisted are allowed to post to the server. So any domains that the site is served over should be added to the list. However, if no referer is found, the session is reset, which will occur with a page reload. This helps protect against XSS attacks.

COOKIELESS['HOSTS'] = ['localhost', ]

5. Further security option to not find and persist cookie based sessions as cookieless ones since these may be tied to a user or other data. Instead new sessions are created for tying to cookieless data. This reduces the risk of cookieless allowing capture of a user's session - and hence privilege escalation attacks.

COOKIELESS['NO_COOKIE_PERSIST'] = True

6. Further security option to only keep a session for accessing a specific URL 

COOKIELESS['URL_SPECIFIC'] = True

7. Delete any cookies that are found for a no_cookies decorated URL (could be ones set by other URLs)

COOKIELESS['DELETE_COOKIES'] = False

Tests
-----

The test suite sets up a simple application to test cookies manually, and to run the functional tests against.

Note that if the egg is installed normally, the cookieless.tests application will probably not have write permissions
so to run the tests install from src:

bin/pip install -e git+https://github.com/edcrewe/django-cookieless#egg=django-cookieless

Or move the tests application out and install separately as a django app.
Then run via:

bin/django-admin.py or manage.py test cookieless --settings="cookieless.tests.settings"

Note: cookieless/decorator.py

Because the django test browser has some session implementation specific mocking, 
it fails to work if used directly against cookieless, so to stop it breaking other tests
cookieless checks to see if the django admin command has been called with the 'test' argument and sets settings.TESTING = True, and doesnt decorate with no_cookies if so.

To override this automatic disabling setting, just add TESTING = False, to your test settings.
