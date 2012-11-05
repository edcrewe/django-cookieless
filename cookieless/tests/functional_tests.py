from django.conf import settings
from django.utils import unittest
from django.test.client import RequestFactory

class FuncTestCase(unittest.TestCase):
    """
    Check the session id encryption is working OK
    """
    # urls = 'django-cookieless.test_urls'
    
    def setUp():
        """ Get a session and a crypt_session """
        self.factory = RequestFactory()

    def test_navigate():
        """ Confirm session is maintained without cookie """
        
        return

