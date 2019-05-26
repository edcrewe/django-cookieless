"""Add {% load cookieless %}  after base to use these in a template
"""

from django.conf import settings
from django import template
from django.template.defaultfilters import stringfilter, striptags
from django.utils.safestring import mark_safe
from django.utils.html import escape

from cookieless.cryptsession import CryptSession

register = template.Library()


class BaseSessionNode(template.Node):
    def __init__(self):
        self.request_var = template.Variable("request")
        self._sesh = CryptSession()

    def get_key(self, context):
        request = self.request_var.resolve(context)
        if request.session.session_key:
            return self._sesh.encrypt(request, request.session.session_key)
        else:
            return ""


class FormSessionNode(BaseSessionNode):
    def render(self, context):
        session_key = self.get_key(context)
        if session_key:
            html = '<input type="hidden" name="%s" value="%s" />'
            return mark_safe(html % (settings.SESSION_COOKIE_NAME, session_key))
        else:
            return ""


def session_form(parser, token):
    return FormSessionNode()


register.tag("session_token", session_form)


class URLSessionNode(BaseSessionNode):
    def __init__(self, url):
        super(URLSessionNode, self).__init__()
        self.url = self._sesh.prepare_url(url.replace('"', ""))

    def render(self, context):
        session_key = self.get_key(context)
        if session_key:
            html = '"%s%s=%s"'
            return mark_safe(
                html % (self.url, settings.SESSION_COOKIE_NAME, session_key)
            )
        else:
            return ""


def session_filter(parser, token):
    try:
        taglist = token.split_contents()  # Not really useful
    except ValueError:
        raise template.TemplateSyntaxError("%r error" % token.contents.split()[0])
    if len(taglist) > 1:
        url = taglist[1]
    return URLSessionNode(url)


register.tag("session_url", session_filter)
