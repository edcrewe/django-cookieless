import unittest

from django.conf import settings

from cookieless.tests.base import BaseFuncTestCase
from cookieless.middleware import cookieless_signal

signal = (None, None)
scounter = 0


def signal_me(**kwargs):
    """ Method to tie to signal for tests """
    global scounter, signal
    request = kwargs.get("sender", "")
    created = kwargs.get("created", "")
    signal = (request, created)
    scounter += 1


# Send signals to method for testing
cookieless_signal.connect(signal_me)


class SignalFuncTestCase(BaseFuncTestCase):
    """
    Check the cookie is not present but session data is maintained
    Uses the tests.settings urls and views to functionally test

    NB: test client session and cookies doesnt work with cookieless
    So SERVER_NAME is used to disable cookieless for general tests
    Hence SERVER_NAME has to be changed to enable tests here ...
    """

    def test_signal(self):
        """ Check that the signal is fired when a cookieless session is
            created or modified
        """
        global scounter, signal
        # Must reset signal since other tests will have triggered it
        # Because its set at module loading time
        signal = (None, None)
        scounter = 0
        self.assertEqual(signal, (None, None))
        response = self.browser.get("/index.html")
        session, session_id = self.get_session(response)
        self.assertNotEqual(signal, (None, None))
        # Check signal sent once and its created = True
        self.assertEqual(scounter, 1)
        self.assertTrue(signal[1])
        # Post back to the page and check update signal fired
        # but created = False
        postdict = {self.skey: session_id}
        response = self.browser.post("/index.html", postdict)
        self.assertEqual(scounter, 2)
        self.assertFalse(signal[1])
