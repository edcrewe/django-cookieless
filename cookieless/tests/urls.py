from django.conf.urls import patterns, include, url
from cookieless.tests.views import MyClassView
from cookieless.tests.views import my_function_view, my_plain_view

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

from cookieless.decorators import no_cookies

urlpatterns = patterns('',
    # Examples views:
    url(r'^function-view.html', no_cookies(my_function_view), name='function_view'),
    url(r'^plain-view.html', no_cookies(my_plain_view), name='plain_view'),
    url(r'^index.html', no_cookies(MyClassView.as_view()), name='class_view'),
    url(r'^$', no_cookies(MyClassView.as_view()), name='class_view'),
    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
