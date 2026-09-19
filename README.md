# Django Cookieless

Ed Crewe - Sept 2026

## Overview

This package provides a sessions implementation and decorator class for views to
allow forms to maintain state without using cookies, by posting the session ID
between forms, or via URLs.

Django requires cookies to maintain sessions, and hence for authorisation.

This package is designed to cater for anonymous user session maintenance,
without cookies.

**Warning:** there are security issues with this, since it is not possible to
use CSRF protection without session cookies to maintain a separate token from
that passed via the URL or form posts.

However there are cases when forms are used on a public site where setting
cookies is not desirable, for example due to
[privacy legislation](http://www.ico.gov.uk/), since technically they are not
required for anonymous users to respond to forms. So if used, this may
necessitate requesting permission to set cookies from the user.

Hence this package was devised to allow Django to deliver multipage forms,
without using cookies.

To ameliorate the security implications, a whitelist of allowed domains can be
set in the configuration.

Usage can also be restricted to a particular URL.

As another safety measure, handling of GET requests can be turned off, so that
the encrypted session ID is not present in URLs.

Please note, it is not advisable to use this package without some form of the
above restrictions being in place.

For the purposes of using both cookie based and cookieless sessions together,
there is a custom `cookieless_signal(sender=request, created)` and a
`no_cookies` flag when cookieless sessions are saved.

Both cater for hooking up custom code for handling these less secure sessions.

The package provides a decorator utility to turn off cookie setting for
particular views, which also sets the `csrf_exempt` flag.

The package also handles the case of session handling for anonymous users with
cookies disabled in the browser.

You can decorate views to prevent them setting cookies, while still retaining
the use of sessions. Usually this is easiest done in the `urls.py` of your core
application.

```python
from cookieless.decorators import no_cookies

urlpatterns = [
    path("somewhere/index", no_cookies(views.home)),
    re_path(r"^somewhere/page/(\d{1,6})$", no_cookies(views.page)),
]
```

Note that if a number of browser tabs are open on to a site with cookieless,
they will each maintain a completely separate session, since without cookies
the session is tied to the session posted from the pages accessed, not the
client as a whole.

In cases where this is not the desired behaviour, then it can be reduced by
using URL rewriting to make any links to open other windows pass session
across. However this also means that potentially a session can be shared across
browsers.

## Installation

To install add the package via pip or other build tool, for example:

```bash
python -m pip install django-cookieless
```

Then replace the standard session middleware in your settings:

```python
MIDDLEWARE = [
    # "django.contrib.sessions.middleware.SessionMiddleware",
    "cookieless.middleware.CookielessSessionMiddleware",
    ...
]
```

The following settings control behaviour, see the example settings file.

1. Rewrite the response automatically rather than using manual
   `<% session_token %> <% session_url %>`.

   ```python
   COOKIELESS["REWRITE"] = True
   ```

2. Rewrite URLs to add a session ID for `no_cookies` decorated views. If this
   is false then all page navigation must be via form posts.

   ```python
   COOKIELESS["USE_GET"] = True
   ```

3. Use client IP and user agent to encrypt the session key, to add some sort
   of CSRF protection given that standard CSRF has to be disabled without
   cookies.

   ```python
   COOKIELESS["CLIENT_ID"] = True
   ```

4. If this list is populated then only hosts that are specifically whitelisted
   are allowed to post to the server. Any domains that the site is served over
   should be added to the list. However, if no referrer is found, the session
   is reset, which will occur with a page reload. This helps protect against
   XSS attacks.

   ```python
   COOKIELESS["HOSTS"] = ["localhost"]
   ```

5. Further security option to avoid finding and persisting cookie based
   sessions as cookieless ones, since these may be tied to a user or other
   data. Instead new sessions are created for cookieless data. This reduces the
   risk of cookieless allowing capture of a user's session, and hence privilege
   escalation attacks.

   ```python
   COOKIELESS["NO_COOKIE_PERSIST"] = True
   ```

6. Further security option to only keep a session for accessing a specific URL.

   ```python
   COOKIELESS["URL_SPECIFIC"] = True
   ```

7. Delete any cookies that are found for a `no_cookies` decorated URL, for
   example ones set by other URLs.

   ```python
   COOKIELESS["DELETE_COOKIES"] = False
   ```

8. Optional, set an explicit shared cipher key for session token encryption.
   If omitted, cookieless derives a stable key from Django `SECRET_KEY`.

   ```python
   COOKIELESS["CIPHER_KEY"] = "shared secret or a fernet key"
   ```

## Tests

The test suite sets up a simple application to test cookies manually, and to
run the functional tests against.

To run the tests, you may want to install from source, or your branch:

```bash
python -m pip install -e .
```

Then run via:

```bash
python -m django test cookieless.tests --settings=cookieless.tests.settings
```

Tested on Django 6.1 and 5.2 with Python 3.14, and in CI on Python
3.13/Django 6.1 and Python 3.12/Django 5.2.

The package was changed from a namespace package due to the issue with pip not
installing `__init__` for running tests when it does an `nspkg.pth` file
instead.

## cookieless/decorator.py

Because the Django test browser has some session implementation specific
mocking, it fails to work if used directly against cookieless. To stop it
breaking other tests, cookieless checks whether `django-admin` has been called
with the `test` argument and sets `settings.TESTING = True`, and does not
decorate with `no_cookies` if so.

To override this automatic disabling setting, add `TESTING = False` to your
test settings.
