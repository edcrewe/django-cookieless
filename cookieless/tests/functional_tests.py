from django.conf import settings
from django.utils import unittest
from django.test.client import Client
from django.test.client import RequestFactory
from django.utils.importlib import import_module

from cookieless.utils import CryptSession
from cookieless.config import DEFAULT_SETTINGS

class FuncTestCase(unittest.TestCase):
    """
    Check the cookie is not present but session data is maintained
    Uses the tests.settings urls and views to functionally test

    NB: test client session and cookies doesnt work with cookieless
    So SERVER_NAME is used to disable cookieless for general tests
    Hence SERVER_NAME has to be changed to enable tests here ...
    """
    
    def setUp(self):
        """ Turn of HOSTS check and setup reusable attributes """
        self.settings = getattr(settings, 'COOKIELESS', DEFAULT_SETTINGS)
        self.settings['HOSTS'] = []
        self.browser = Client()
        self.browser.request(SERVER_NAME='enable_testserver')
        self.engine = import_module(settings.SESSION_ENGINE)
        self.crypt_sesh = CryptSession()
        self.factory = RequestFactory()
        self.skey = settings.SESSION_COOKIE_NAME
        self.hidden = '<input type="hidden" name="%s" value="' % self.skey

    def get_session(self, response):
        """ Extract id from response and retrieve session """
        parts = response.content.split(self.hidden)
        if len(parts) == 1:
            return {}, ''
        parts = parts[1].split('"')
        session_id = parts[0]
        request = self.factory.get('/', SERVER_NAME='enable_testserver')
        session_key = self.crypt_sesh.decrypt(request, session_id)
        try:
            session = self.engine.SessionStore(session_key)
        except:
            session = self.engine.SessionStore()
        return session, session_id
        
    def test_session_in_tags_html(self):
        """ Confirm session is generated in html via tags """
        self.settings['REWRITE'] = False
        response = self.browser.get('/', SERVER_NAME='enable_testserver')
        url = '?%s=' % settings.SESSION_COOKIE_NAME
        # Check form session id is set
        self.assertTrue(self.hidden in response.content)
        self.assertTrue(url in response.content)

    def test_session_in_rewritten_html(self):
        """ Confirm session is rewritten into html """
        self.settings['REWRITE'] = True
        response = self.browser.get('/plain-view.html', 
                                    SERVER_NAME='enable_testserver')
        url = '?%s=' % settings.SESSION_COOKIE_NAME
        # Check form session id is set
        self.assertTrue(self.hidden in response.content)
        self.assertTrue(url in response.content)

    def test_session_no_url_rewrite_option(self):
        """ Confirm session is rewritten into html """
        self.settings['REWRITE'] = True
        self.settings['USE_GET'] = False
        response = self.browser.get('/plain-view.html', 
                                    SERVER_NAME='enable_testserver')
        url = '?%s=' % settings.SESSION_COOKIE_NAME
        # Check form session id is set but urls aren't
        self.assertTrue(self.hidden in response.content)
        self.assertTrue(url not in response.content)

    def test_disabled_for_standard_test_browser(self):
        """ Confirm standard test browser doesnt use cookieless """
        self.settings['REWRITE'] = True
        response = self.browser.get('/plain-view.html')
        self.assertTrue(self.hidden not in response.content)

    def test_session_retained(self):
        """ Get the first page then retrieve the session
            and confirm it is retained and populated in the second page
        """
        self.settings['REWRITE'] = False
        self.settings['URL_SPECIFIC'] = False
        response = self.browser.get('/', SERVER_NAME='enable_testserver')
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
        self.settings['REWRITE'] = False
        self.settings['URL_SPECIFIC'] = True
        response = self.browser.get('/', SERVER_NAME='enable_testserver')
        session, session_id = self.get_session(response)
        self.assertTrue('classview' in session.keys())
        self.assertEqual(len(session.keys()), 2)
        # Post form to second page where session is restarted
        postdict = { self.skey : session_id, }
        self.browser.post("/function-view.html", postdict,
                          SERVER_NAME='enable_testserver')
        session = self.engine.SessionStore(session.session_key)
        self.assertTrue('funcview' not in session.keys())
        self.assertEqual(len(session.keys()), 2)
        # Post form back to first page where session is retained
        postdict = { self.skey : session_id, }
        self.browser.post("/", postdict, SERVER_NAME='enable_testserver')
        session = self.engine.SessionStore(session.session_key)
        self.assertEqual(len(session.keys()), 3)


    def test_session_not_retained_other_host(self):
        """ Get the first page then retrieve the session
            and confirm it is no longer retained if the host changes
        """
        self.settings['REWRITE'] = False
        self.settings['URL_SPECIFIC'] = True
        response = self.browser.get('/', SERVER_NAME='enable_testserver')
        session, session_id = self.get_session(response)
        self.assertTrue('classview' in session.keys())
        self.assertEqual(len(session.keys()), 2)
        # Post form back to first page where other session is started
        postdict = { self.skey : session_id, }
        self.browser.post("/", postdict)
        session = self.engine.SessionStore(session.session_key)
        self.assertEqual(len(session.keys()), 2)
        # Post form back to first page where session is retained
        postdict = { self.skey : session_id, }
        self.browser.post("/", postdict, SERVER_NAME='enable_testserver')
        session = self.engine.SessionStore(session.session_key)
        self.assertEqual(len(session.keys()), 3)
