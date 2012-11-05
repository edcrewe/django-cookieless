from django.conf import settings
from django.utils import unittest
from django.test.client import RequestFactory

from cookieless.utils import CryptSession


class CryptTestCase(unittest.TestCase):
    """
    Check the session id encryption is working OK
    """
    # urls = 'django-cookieless.test_urls'
    
    def setUp():
        """ Get a session and a crypt_session """
        self.engine = import_module(settings.SESSION_ENGINE)
        self.crypt_sesh = CryptSession()
        self.factory = RequestFactory()
        
    def crypt_ok(request=None):
        """ Check encryption works with various settings """
        request = self.factory.get('/render/')
        session = engine.SessionStore()
        sessionid = self.crypt_sesh.encrypt(request, session.session_key)
        session_key = self.crypt_sesh.encrypt(request, sessionid)
        return session.session_key, session_key

    def test_default():
        settings.COOKIELESS_CLIENT_ID = False
        settings.COOKIELESS_HOSTS = []
        keys = self.crypt_ok()
        self.assertEqual(*keys)

    def test_client_id():
        settings.COOKIELESS_CLIENT_ID = True
        settings.COOKIELESS_HOSTS = []
        keys = self.crypt_ok()
        self.assertEqual(*keys)

    def test_hosts_check():
        settings.COOKIELESS_CLIENT_ID = False
        settings.COOKIELESS_HOSTS = ['localhost', ]
        keys = self.crypt_ok()
        self.assertEqual(*keys)


