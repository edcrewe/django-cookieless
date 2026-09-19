import unittest
from importlib import import_module

from django.conf import settings
from django.test.client import RequestFactory
from django.template import Context, Template, TemplateSyntaxError
from django.test import SimpleTestCase

from cookieless import cookieless_contains_class
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
        self.settings["HOSTS"] = ["localhost"]
        request = self.factory.get("/")
        request.META["HTTP_REFERER"] = "http://localhost:12345/foobar"
        keys = self.crypt_ok(request)
        self.assertEqual(*keys)

    def test_test_client(self):
        """Cookieless can cause fail of test browser so check it"""
        self.browser = Client()
        self.browser.request()
        self.assertTrue(self.browser)

    def test_hosts_check_missing_referer_resets_session(self):
        self.settings["CLIENT_ID"] = False
        self.settings["HOSTS"] = ["localhost"]
        request = self.factory.get("/")
        session = self.engine.SessionStore()
        session.create()
        sessionid = self.crypt_sesh.encrypt(request, session.session_key)
        self.assertEqual(self.crypt_sesh.decrypt(request, sessionid), "")

    def test_hosts_check_rejects_unauthorised_host(self):
        self.settings["CLIENT_ID"] = False
        self.settings["HOSTS"] = ["localhost"]
        request = self.factory.get("/")
        session = self.engine.SessionStore()
        session.create()
        sessionid = self.crypt_sesh.encrypt(request, session.session_key)
        bad_request = self.factory.get("/", HTTP_REFERER="http://example.org/foobar")
        with self.assertRaises(Exception):
            self.crypt_sesh.decrypt(bad_request, sessionid)


class TemplateTagTestCase(SimpleTestCase):
    def setUp(self):
        self.engine = import_module(settings.SESSION_ENGINE)
        self.factory = RequestFactory()

    def test_session_url_requires_url_arg(self):
        with self.assertRaises(TemplateSyntaxError):
            Template("{% load cookieless_tags %}{% session_url %}")

    def test_session_url_renders_with_session(self):
        request = self.factory.get("/")
        request.session = self.engine.SessionStore()
        request.session.create()
        rendered = Template(
            '{% load cookieless_tags %}{% session_url "/function-view.html" %}'
        ).render(Context({"request": request}))
        self.assertTrue("/function-view.html?" in rendered)
        self.assertTrue(f"{settings.SESSION_COOKIE_NAME}=" in rendered)


class InitPatchTestCase(SimpleTestCase):
    def test_contains_class_accepts_session_middleware(self):
        self.assertTrue(cookieless_contains_class(
            "django.contrib.sessions.middleware.SessionMiddleware", []
        ))

    def test_contains_class_accepts_candidate_match(self):
        self.assertTrue(cookieless_contains_class(
            "custom.middleware.Example", ["custom.middleware.Example"]
        ))

    def test_contains_class_returns_none_for_miss(self):
        self.assertIsNone(cookieless_contains_class(
            "custom.middleware.Missing", ["custom.middleware.Example"]
        ))
