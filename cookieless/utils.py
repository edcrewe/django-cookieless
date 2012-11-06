""" Obscure the session id when passing it around in HTML """
from django.conf import settings
from urlparse import urlparse
from cookieless.xteacrypt import crypt

class CryptSession(object):
    """ Tool to generate encrypted session id for 
        middleware or templatetags 
    """
    def __init__(self):
        self.secret = settings.SECRET_KEY[:16]

    def prepare_url(self, url):
        patt = None
        if url.find('?') == -1:
            patt = '%s?'
        else:
            patt = '%s&amp;'
        return patt % (url,)

    def encrypt(self, request, sessionid):
        """ Avoid showing plain sessionids """  
        if not sessionid:
            return ''
        secret = self._secret(request)
        return crypt(secret, sessionid).encode('hex')

    def decrypt(self, request, sessionid):
        """ Avoid showing plain sessionids 
            Optionally require that a referer exists and matches the 
            whitelist, or reset the session
        """
        if not sessionid:
            return ''
        secret = self._secret(request)
        if getattr(settings, 'COOKIELESS_HOSTS', []):
            referer = request.META.get('HTTP_REFERER', 'None')
            if referer == 'None':
                # End session unless a referer is passed
                return ''
            url = urlparse(referer)
            if url.hostname not in settings.COOKIELESS_HOSTS:
                err = '%s is unauthorised' % url.hostname
                raise Exception(err)
        return crypt(secret, sessionid.decode('hex'))

    def key_tuple(self, request):
        """ For use in generated html """
        return (settings.SESSION_COOKIE_NAME, 
                self.encrypt(request, request.session.session_key))

    def _secret(self, request):
        """ optionally make secret client or url dependent
            NB: Needs to be at least 16 characters so add secret to META data
        """
        secret = self.secret
        specific = ''
        if getattr(settings, 'COOKIELESS_URL_SPECIFIC', False):
            specific += request.META.get('SERVER_NAME', '')
            specific += request.META.get('PATH_INFO', '')
        if getattr(settings, 'COOKIELESS_CLIENT_ID', False):
            specific += request.META.get('REMOTE_ADDR', '127.0.0.1') 
            specific += request.META.get('HTTP_USER_AGENT', 'unknown browser')
        if specific:
            secret = crypt(secret, specific + self.secret) 
            secret = secret.encode('hex')[-16:]
        return secret
