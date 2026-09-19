# Create your views here.

from django.views.generic import TemplateView
from django.http import HttpResponse
from django.http import HttpResponseRedirect
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


def my_cookie_view(request):
    """Undecorated view to exercise standard session middleware behaviour."""
    request.session["cookieview"] = "my_cookie_view"
    return HttpResponse("<html><body><h1>Cookie view</h1></body></html>")


def my_redirect_same_host_view(request):
    """Redirect to same host for cookieless URL rewrite checks."""
    return HttpResponseRedirect("http://localhost/index.html")


def my_redirect_other_host_view(request):
    """Redirect to other host to ensure cookieless does not rewrite it."""
    return HttpResponseRedirect("http://example.org/index.html")


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
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["session_data"] = session_data(self.request)
        return context

    def post(self, request, *args, **kwargs):
        """ A post method is required for django class views that don't have it
            or they throw django.http.HttpResponseNotAllowed and wipe response.content
            (Or at least they do for the test browser)
        """
        context = super().get_context_data(**kwargs)
        context["session_data"] = session_data(self.request)
        return self.render_to_response(context)
