##### django-cookieless #####

COOKIELESS = {}

# Rewriting the response automatically rather than use manual <% session_token %> <% session_url %>
COOKIELESS["REWRITE"] = True

# Rewrite URLs to add session id for no_cookies decorated views
# (if False then all page navigation must be via form posts)
COOKIELESS["USE_GET"] = True

# NB: Need to add django.core.context_processors.request if using manual tags
# so its available for templatetags/cookieless
if not COOKIELESS["REWRITE"]:
    import django.conf.global_settings as DEFAULT_SETTINGS

    TEMPLATE_CONTEXT_PROCESSORS = DEFAULT_SETTINGS.TEMPLATE_CONTEXT_PROCESSORS + (
        "django.core.context_processors.request",
    )

# Use client ip and browser to encode session key, to add some CSRF protection without being able to use cookies.
COOKIELESS["CLIENT_ID"] = True

# If this list is populated then only hosts that are specifically whitelisted#  are allowed to post to the server. So any domains that the site is served # over should be added to the list. This helps protect against XSS attacks.
COOKIELESS["HOSTS"] = ["localhost"]

# Further security option to not find and persist cookie based sessions as cookieless ones
# since these may be tied to a user or other data
COOKIELESS["NO_COOKIE_PERSIST"] = True

# Further security option to only keep a session for accessing a specific URL
COOKIELESS["URL_SPECIFIC"] = True

# Delete any cookies found when on a no_cookies URL
COOKIELESS["DELETE_COOKIES"]

# Specify what directory should be excluded from being cookieless
# Most common setting is to exclude your admin directory
COOKIELESS["EXCLUDE_DIR"] = "/admin"

#############################

# Settings to be used when running unit tests
# python manage.py test --settings=django-cookieless.test_settings django-cookieless

DATABASE_ENGINE = (
    ""
)  # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
DATABASE_NAME = ""  # Or path to database file if using sqlite3.
DATABASE_USER = ""  # Not used with sqlite3.
DATABASE_PASSWORD = ""  # Not used with sqlite3.
DATABASE_HOST = ""  # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ""  # Set to empty string for default. Not used with sqlite3.

INSTALLED_APPS = (
    # Put any other apps that your app depends on here
    "cookieless",
)
SITE_ID = 1

# This merely needs to be present - as long as your test case specifies a
# urls attribute, it does not need to be populated.
ROOT_URLCONF = ""
