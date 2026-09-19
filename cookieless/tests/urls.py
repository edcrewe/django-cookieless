from django.urls import path
from cookieless.tests.views import MyClassView
from cookieless.tests.views import (
    my_binary_view,
    my_cookie_view,
    my_function_view,
    my_link_rewrite_view,
    my_plain_view,
    my_redirect_other_host_view,
    my_redirect_same_host_view,
)

# Uncomment the next two lines to enable the admin:
from django.contrib import admin

admin.autodiscover()

from cookieless.decorators import no_cookies

urlpatterns = [
    # Examples views:
    path("function-view.html", no_cookies(my_function_view)),
    path("plain-view.html", no_cookies(my_plain_view)),
    path("binary-view.bin", no_cookies(my_binary_view)),
    path("link-view.html", no_cookies(my_link_rewrite_view)),
    path("redirect-same-host.html", no_cookies(my_redirect_same_host_view)),
    path("redirect-other-host.html", no_cookies(my_redirect_other_host_view)),
    path("index.html", no_cookies(MyClassView.as_view())),
    path("cookie-view.html", my_cookie_view),
    path("", no_cookies(MyClassView.as_view())),
    # Uncomment the next line to enable the admin:
    path("admin/", admin.site.urls),
]
