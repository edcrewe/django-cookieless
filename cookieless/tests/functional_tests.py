from django.conf import settings
from django.utils import unittest
from django.test.client import Client
from django.test.client import RequestFactory
from django.utils.importlib import import_module

from cookieless.utils import CryptSession

class FuncTestCase(unittest.TestCase):
    """
    Check the cookie is not present but session data is maintained
    Uses the tests.settings urls and views to functionally test

    NB: test client session is just an empty dictionary so cant be used for tests
    """
    
    def setUp(self):
        """ Turn of HOSTS check and setup reusable attributes """
        settings.COOKIELESS_HOSTS = []
        self.browser = Client()
        self.engine = import_module(settings.SESSION_ENGINE)
        self.crypt_sesh = CryptSession()
        self.factory = RequestFactory()
        self.skey = settings.SESSION_COOKIE_NAME
        self.hidden = '<input type="hidden" name="%s" value="' % self.skey

    def get_session(self, response):
        """ Extract id from response and retrieve session """
        parts = response.content.split(self.hidden)
        parts = parts[1].split('"')
        session_id = parts[0]
        request = self.factory.get('/')
        session_key = self.crypt_sesh.decrypt(request, session_id)
        session = self.engine.SessionStore(session_key)
        return session, session_id
        
    def test_session_in_tags_html(self):
        """ Confirm session is generated in html via tags """
        settings.COOKIELESS_REWRITE = False
        response = self.browser.get('/')
        url = '?%s=' % settings.SESSION_COOKIE_NAME
        # Check form session id is set
        self.assertTrue(self.hidden in response.content)
        self.assertTrue(url in response.content)

    def test_session_in_rewritten_html(self):
        """ Confirm session is rewritten into html """
        settings.COOKIELESS_REWRITE = True
        response = self.browser.get('/plain-view.html')
        url = '?%s=' % settings.SESSION_COOKIE_NAME
        # Check form session id is set
        self.assertTrue(self.hidden in response.content)
        self.assertTrue(url in response.content)

    def test_session_no_url_rewrite_option(self):
        """ Confirm session is rewritten into html """
        settings.COOKIELESS_REWRITE = True
        settings.COOKIELESS_USE_GET = False
        response = self.browser.get('/plain-view.html')
        url = '?%s=' % settings.SESSION_COOKIE_NAME
        # Check form session id is set but urls aren't
        self.assertTrue(self.hidden in response.content)
        self.assertTrue(url not in response.content)

    def test_session_retained(self):
        """ Get the first page then retrieve the session
            and confirm it is retained and populated in the second page
        """
        settings.COOKIELESS_REWRITE = False
        settings.COOKIELESS_URL_SPECIFIC = False
        response = self.browser.get('/')
        session, session_id = self.get_session(response)
        self.assertTrue('classview' in session.keys())
        self.assertEqual(len(session.keys()), 2)
        # Post form to second page
        postdict = { self.skey : session_id, }
        self.browser.post("/function-view.html", postdict)
        # Get session again
        session = self.engine.SessionStore(session.session_key)
        self.assertTrue('funcview' in session.keys())
        self.assertEqual(len(session.keys()), 3)

    def test_session_not_retained_other_url(self):
        """ Get the first page then retrieve the session
            and confirm it is no longer retained if the url is not maintained
        """
        settings.COOKIELESS_REWRITE = False
        settings.COOKIELESS_URL_SPECIFIC = True
        response = self.browser.get('/')
        session, session_id = self.get_session(response)
        self.assertTrue('classview' in session.keys())
        self.assertEqual(len(session.keys()), 2)
        # Post form to second page where session is restarted
        postdict = { self.skey : session_id, }
        self.browser.post("/function-view.html", postdict)
        session = self.engine.SessionStore(session.session_key)
        self.assertTrue('funcview' not in session.keys())
        self.assertEqual(len(session.keys()), 2)
        # Post form back to first page where session is retained
        postdict = { self.skey : session_id, }
        self.browser.post("/", postdict)
        session = self.engine.SessionStore(session.session_key)
        self.assertEqual(len(session.keys()), 3)
