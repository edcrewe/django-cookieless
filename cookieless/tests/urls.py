from django.conf.urls import patterns, include, url
from cookieless.tests.views import MyClassView
from cookieless.tests.views import my_function_view

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

from cookieless.decorators import no_cookies

urlpatterns = patterns('',
    # Examples:
    url(r'^function-view.html', no_cookies(my_function_view), name='function_view'),
    url(r'^$', no_cookies(MyClassView.as_view()), name='class_view'),

    # url(r'^dummy/', include('dummy.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
