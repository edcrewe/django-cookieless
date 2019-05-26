from importlib import import_module

from django.conf import settings
from django.test.client import Client
from django.test.client import RequestFactory
from django.test import TestCase

from cookieless.cryptsession import CryptSession
from cookieless.config import DEFAULT_SETTINGS


class BaseFuncTestCase(TestCase):
    """
    Utitlity methods to pull stuff out of session etc.
    """

    def setUp(self):
        """ Turn of HOSTS check and setup reusable attributes """
        self.settings = getattr(settings, "COOKIELESS", DEFAULT_SETTINGS)
        self.settings["HOSTS"] = []
        self.browser = Client()
        self.browser.request()
        self.engine = import_module(settings.SESSION_ENGINE)
        self.crypt_sesh = CryptSession()
        self.factory = RequestFactory()
        self.skey = settings.SESSION_COOKIE_NAME
        # This is a bit crap - because matching is fragile and also its
        # reused to split up and grab the session id - TODO: replace with regex
        self.hidden = '<input type="hidden" name="%s" value="' % self.skey

    def get_session(self, response, url="/", agent="unknown browser"):
        """ Extract id from response and retrieve session """
        # post or get
        parts = ""
        if not response.content:
            print("RESPONSE FAILED: {}".format(response.__class__))
        else:
            content = response.content.decode()
        if self.hidden in content:
            splitter = self.hidden
        else:
            splitter = "%s=" % self.skey
        parts = content.split(splitter, 1)
        session_key = ""
        if len(parts) > 1:
            parts = parts[1].split('"', 1)
            session_id = parts[0]
            request = self.factory.get(
                url, REMOTE_ADDR="127.0.0.1", HTTP_USER_AGENT=agent
            )
            try:
                session_key = self.crypt_sesh.decrypt(request, session_id)
            except:
                # Silently start new session in case fake session_id format causes error
                pass
        else:
            session_id = ""
        try:
            session = self.engine.SessionStore(session_key)
        except:
            session = self.engine.SessionStore()
        return session, session_id
