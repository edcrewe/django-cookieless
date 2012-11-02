#-*- coding:utf-8 -*-import time
import re, pdb

from django.conf import settings
from django.utils.cache import patch_vary_headers
from django.utils.http import cookie_date
from django.utils.importlib import import_module
from django.http  import  HttpResponseRedirect
from django.contrib.sessions.middleware import SessionMiddleware
# Obscure the session id when passing it around in HTML
from cookieless.xteacrypt import crypt

LINKS_RE = r'<a(?P<pre_href>[^>]*?)href=["\'](?P<in_href>[^"\']*?)(?P<anchor>#\S+)?["\'](?P<post_href>[^>]*?)>'


class CookielessSessionMiddleware(object):
    """ Django snippets julio carlos and Ivscar 
        http://djangosnippets.org/snippets/1540/

        Plus django.session.middleware combined
        To use, replace 
        'django.contrib.sessions.middleware.SessionMiddleware'
        with 'cookieless.middleware.CookielessSessionMiddleware'

        NB: Remember only decorated methods are cookieless
    """

    def __init__(self):
        """ Add regex for auto inserts and an instance of
            the standard django.contrib.sessions middleware
        """
        self._re_links = re.compile(LINKS_RE, re.I)
        self._re_forms = re.compile('</form>', re.I)

        self.standard_session = SessionMiddleware()
        self.secret = settings.SECRET_KEY[:16]

    def process_request(self, request):
        """ Check if we have the session key from a cookie, 
            if not check post, and get if allowed
        """
        name = settings.SESSION_COOKIE_NAME
        session_key = request.COOKIES.get(name, '')
        if not session_key:
            session_key = self._decrypt(request.POST.get(name, None))
            if not session_key and getattr(settings, 'COOKIELESS_USE_GET', False):
                session_key = self._decrypt(request.GET.get(name, ''))
            if session_key:
                request.COOKIES[name] = session_key        
        engine = import_module(settings.SESSION_ENGINE)
        request.session = engine.SessionStore(session_key)

    def process_response(self, request, response):
        """
        Copied from contrib.session.middleware with no_cookies switch added ...
        If request.session was modified, or if the configuration is to save the
        session every time, save the changes and set a session cookie.
        """
        if getattr(request, 'no_cookies', False):
            response.cookies.clear()
            # cookieless - do same as standard process response
            #              but dont set the cookie
            if getattr(settings, 'COOKIELESS_REWRITE', False):
                response = self.nocookies_response(request, response)
            try:
                accessed = request.session.accessed
                modified = request.session.modified
            except AttributeError:
                pass
            else:
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
            return response
        else:
            raise Exception('LOST no_cookies')
            return self.standard_session.process_response(request, response)

    def _prepare_url(self, url):
        patt = None
        if url.find('?') == -1:
            patt = '%s?'
        else:
            patt = '%s&amp;'
        return patt % (url,)

    def _encrypt(self, sessionid):
        """ Avoid showing plain sessionids """  
        if not sessionid:
            return ''
        return crypt(self.secret, sessionid).encode('hex')

    def _decrypt(self, sessionid):
        """ Avoid showing plain sessionids """  
        if not sessionid:
            return ''
        return crypt(self.secret, sessionid.decode('hex'))

    def nocookies_response(self, request, response):
        """ Option to rewrite forms and urls to add session automatically """
        name = settings.SESSION_COOKIE_NAME
        session_key = ''
        if request.session.session_key and not request.path.startswith("/admin"):  
            session_key = self._encrypt(request.session.session_key) 

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

            if getattr(settings, 'COOKIELESS_USE_GET', False):            
                try:
                    response.content = self._re_links.sub(new_url, response.content)
                except:
                    pass

            repl_form = '''<div><input type="hidden" name="%s" value="%s" />
                           </div></form>'''
            repl_form = repl_form % (name, session_key)

            try:
                response.content = self._re_forms.sub(repl_form, response.content)
            except:
                pass
            return response
        else:
            return response        



#    def process_view(self, request, callback, callback_args, callback_kwargs):
#        if getattr(callback, 'no_cookies', True):
#            return None

