import unittest
from importlib import import_module

from django.conf import settings
from django.test.client import RequestFactory

from cookieless.cryptsession import CryptSession
from cookieless.config import DEFAULT_SETTINGS

from django.test.client import Client


class CryptTestCase(unittest.TestCase):
    """
    Check the session id encryption is working OK
    """

    # urls = 'django-cookieless.test_urls'

    def setUp(self):
        """ Get a session and a crypt_session """
        self.settings = getattr(settings, "COOKIELESS", DEFAULT_SETTINGS)
        self.engine = import_module(settings.SESSION_ENGINE)
        self.crypt_sesh = CryptSession()
        self.factory = RequestFactory()

    def crypt_ok(self, request=None):
        """ Check encryption works with various settings """
        if not request:
            request = self.factory.get("/")
        session = self.engine.SessionStore()
        session.create()
        self.assertNotEqual(session.session_key, None)
        sessionid = self.crypt_sesh.encrypt(request, session.session_key)
        session_key = self.crypt_sesh.decrypt(request, sessionid)
        return session.session_key, session_key

    def test_default(self):
        self.settings["CLIENT_ID"] = False
        self.settings["HOSTS"] = []
        keys = self.crypt_ok()
        self.assertEqual(*keys)

    def test_client_id(self):
        self.settings["CLIENT_ID"] = False
        self.settings["HOSTS"] = []
        keys = self.crypt_ok()
        self.assertEqual(*keys)

    def test_hosts_check(self):
        self.settings["CLIENT_ID"] = False
        request = self.factory.get("/")
        request.META["HTTP_REFERER"] = "http://localhost:12345/foobar"
        settings.COOKIELESS_HOSTS = ["localhost"]
        keys = self.crypt_ok(request)
        self.assertEqual(*keys)

    def test_test_client(self):
        """Cookieless can cause fail of test browser so check it"""
        self.browser = Client()
        self.browser.request()
        self.assertTrue(self.browser)
