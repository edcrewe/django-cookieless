#-*- coding:utf-8 -*-
import time

from django.conf import settings
from django.utils.cache import patch_vary_headers
from django.utils.http import cookie_date
from django.utils.importlib import import_module

from django.http  import  HttpResponseRedirect
import re, pdb
LINKS_RE = r'<a(?P<pre_href>[^>]*?)href=["\'](?P<in_href>[^"\']*?)(?P<anchor>#\S+)?["\'](?P<post_href>[^>]*?)>'


class CookielessSessionMiddleware(object):
    """ Django snippets julio carlos and Ivscar 
        http://djangosnippets.org/snippets/1540/

        Plus django.session.middleware combined
        To use, replace 
        'django.contrib.sessions.middleware.SessionMiddleware'
        with
        'cookieless.middleware.CookielessSessionMiddleware'

        NB: Remember only decorated methods are cookieless
    """

    def __init__(self):

        self._re_links = re.compile(LINKS_RE, re.I)
        self._re_forms = re.compile('</form>', re.I)

    def _prepare_url(self, url):
        patt = None
        if url.find('?') == -1:
            patt = '%s?'
        else:
            patt = '%s&amp;'
        return patt % (url,)

    def process_request(self, request):
        """ Check if we have the session key from a cookie, 
            if not check post, and get if allowed
        """
        name = settings.SESSION_COOKIE_NAME
        session_key = request.COOKIES.get(name, None)
        if request.get('no_cookies', False) or not session_key:
            session_key = request.POST.get(name, None)
            if settings.COOKIELESS_USE_GET:
                session_key = request.GET.get(name, '')
            if not self.no_cookies and session_key:
                request.COOKIES[name] = session_key        
        if session_key:
            engine = import_module(settings.SESSION_ENGINE)
            request.session = engine.SessionStore(session_key)

    def process_response(self, request, response):
        """
        If request.session was modified, or if the configuration is to save the
        session every time, save the changes and set a session cookie.
        """
        try:
            accessed = request.session.accessed
            modified = request.session.modified
        except AttributeError:
            pass
        else:
            if accessed:
                patch_vary_headers(response, ('Cookie',))
            if modified or settings.SESSION_SAVE_EVERY_REQUEST:
                if request.session.get_expire_at_browser_close():
                    max_age = None
                    expires = None
                else:
                    max_age = request.session.get_expiry_age()
                    expires_time = time.time() + max_age
                    expires = cookie_date(expires_time)
                # Save the session data and refresh the client cookie.
                request.session.save()
                if request.get('no_cookies', False): 
                    # cookieless - patch setting of cookies
                    response = self.nocookies_response(request, response)
                else
                    response.set_cookie(settings.SESSION_COOKIE_NAME,
                            request.session.session_key, max_age=max_age,
                            expires=expires, domain=settings.SESSION_COOKIE_DOMAIN,
                            path=settings.SESSION_COOKIE_PATH,
                            secure=settings.SESSION_COOKIE_SECURE or None,
                            httponly=settings.SESSION_COOKIE_HTTPONLY or None)
        return response

    def nocookies_response(self, request, response):
        name = settings.SESSION_COOKIE_NAME
        session_key = ''
        raise Exception(request.session.id)
        if not request.path.startswith("/admin")  and request.session.id:
            try:
                session_key = request.session.id # response.cookies[name].coded_value
                if type(response) is HttpResponseRedirect:
                    if not session_key: 
                        session_key = ""
                    redirect_url = [x[1] for x in response.items() if x[0] == "Location"][0]
                    redirect_url = self._prepare_url(redirect_url)
                    return HttpResponseRedirect('%s%s=%s' % (redirect_url, name, 
                                                             session_key)) 


                def new_url(m):
                    anchor_value = ""
                    if m.groupdict().get("anchor"): 
                        anchor_value = m.groupdict().get("anchor")
                    return_str = '<a%shref="%s%s=%s%s"%s>' % (
                                     m.groupdict()['pre_href'],
                                     self._prepare_url(m.groupdict()['in_href']),
                                     name,
                                     session_key,
                                     anchor_value,
                                     m.groupdict()['post_href']
                                     )
                    return return_str                                 
                response.content = self._re_links.sub(new_url, response.content)


                repl_form = '''<div><input type="hidden" name="%s" value="%s" />
                               </div></form>'''
                repl_form = repl_form % (name, session_key)
                response.content = self._re_forms.sub(repl_form, response.content)

                return response
            except:

                return response
        else:
            return response        


#    def process_view(self, request, callback, callback_args, callback_kwargs):
#        if getattr(callback, 'no_cookies', True):
#            return None

