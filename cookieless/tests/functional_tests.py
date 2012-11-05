from django.conf import settings
from django.utils import unittest
from django.test.client import RequestFactory
from django.test.client import Client

class FuncTestCase(unittest.TestCase):
    """
    Check the cookie is not present but session data is maintained
    Uses the tests.settings urls and views to functionally test
    """
    # urls = 'django-cookieless.test_urls'
    
    def setUp(self):
        """ Get a session and a crypt_session """
        self.factory = RequestFactory()

    def test_navigate(self):
        """ Confirm session is maintained without cookie """
        browser = Client()
        response = browser.get('/')
        hidden = '<input type="hidden" name="%s" value="' % settings.SESSION_COOKIE_NAME
        # Check form session id is set
        self.assertTrue(hidden in response.content)

        return

