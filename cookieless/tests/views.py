# Create your views here.

from django.views.generic import TemplateView
from django.http import HttpResponse
import datetime
from django.utils.html import mark_safe
from cookieless.cryptsession import CryptSession


def session_data(request):
    """ Utility function to display session """
    html = "My session %s.<ul>" % request.session.session_key
    for key, value in request.session.items():
        html += "<li>%s = %s </li>" % (key, value)
    html += "<ul>"
    return mark_safe(html)


def my_function_view(request):
    """ Test function view with manually constructed sesh url """
    request.session["funcview"] = "my_function_view"
    html = "<html><body><h1>Function view</h1>"
    html += '<p><a href="/index.html?%s=%s">Class view</a></p><hr />'
    html = html % CryptSession().key_tuple(request)
    html += session_data(request) + "</body></html>"
    return HttpResponse(html)


def my_plain_view(request):
    """ Test plain html with form and url """
    html = "<html><body><h1>Function view</h1>"
    html += '<p><a href="/">Plain view</a></p><hr />'
    html += '<form action="post"><input type="submit"></form>'
    html += "</body></html>"
    return HttpResponse(html)


class MyClassView(TemplateView):
    """ Test class view - with form """

    template_name = "classview.html"

    def dispatch(self, *args, **kwargs):
        """ Add a session key each time the page is refreshed """
        request = args[0]
        request.session["classview"] = "MyClassView"
        request.session[
            datetime.datetime.now().strftime("%m/%d/%Y-%H:%M:%S")
        ] = "refresh"
        return super(MyClassView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(MyClassView, self).get_context_data(**kwargs)
        context["session_data"] = session_data(self.request)
        return context

    def post(self, request, *args, **kwargs):
        """ A post method is required for django class views that don't have it
            or they throw django.http.HttpResponseNotAllowed and wipe response.content
            (Or at least they do for the test browser)
        """
        context = super(MyClassView, self).get_context_data(**kwargs)
        context["session_data"] = session_data(self.request)
        return self.render_to_response(context)
