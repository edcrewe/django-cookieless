from django.urls import path
from cookieless.tests.views import MyClassView
from cookieless.tests.views import my_function_view, my_plain_view

# Uncomment the next two lines to enable the admin:
from django.contrib import admin

admin.autodiscover()

from cookieless.decorators import no_cookies

urlpatterns = [
    # Examples views:
    path("function-view.html", no_cookies(my_function_view)),
    path("plain-view.html", no_cookies(my_plain_view)),
    path("index.html", no_cookies(MyClassView.as_view())),
    path("", no_cookies(MyClassView.as_view())),
    # Uncomment the next line to enable the admin:
    path("admin/", admin.site.urls),
]
