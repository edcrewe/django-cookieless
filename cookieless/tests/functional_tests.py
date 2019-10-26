import re
import unittest

from gzip import GzipFile
from io import BytesIO

from django.conf import settings

from cookieless.tests.base import BaseFuncTestCase


class FuncTestCase(BaseFuncTestCase):
    """
    Check the cookie is not present but session data is maintained
    Uses the tests.settings urls and views to functionally test

    NB: test client session and cookies doesnt work with cookieless
    So SERVER_NAME is used to disable cookieless for general tests
    Hence SERVER_NAME has to be changed to enable tests here ...
    """

    def test_session_in_tags_html(self):
        """ Confirm session is generated in html via tags """
        self.settings["REWRITE"] = False
        response = self.browser.get("/")
        url = "?%s=" % settings.SESSION_COOKIE_NAME
        # Check form session id is set
        self.assertTrue(self.hidden in response.content.decode())
        self.assertTrue(url in response.content.decode())

    def test_session_in_rewritten_html(self):
        """ Confirm session is rewritten into html """
        self.settings["REWRITE"] = True
        response = self.browser.get("/plain-view.html")
        url = "?%s=" % self.skey
        # Check form session id is set
        self.assertTrue(self.hidden in response.content.decode())
        self.assertTrue(url in response.content.decode())

    def test_session_no_url_rewrite_option(self):
        """ Confirm session is rewritten into html """
        self.settings["REWRITE"] = True
        self.settings["USE_GET"] = False
        response = self.browser.get("/plain-view.html")
        url = "?%s=" % settings.SESSION_COOKIE_NAME
        # Check form session id is set but urls aren't
        self.assertTrue(self.hidden in response.content.decode())
        self.assertTrue(url not in response.content.decode())

    def test_disabled_for_testing_flag(self):
        """ Confirm that normally test browser will not use cookieless """
        self.settings["REWRITE"] = True
        settings.TESTING = True
        response = self.browser.get("/plain-view.html")
        self.assertTrue(self.hidden not in response.content.decode())
        settings.TESTING = False

    def test_session_retained(self):
        """ Get the first page then retrieve the session
            and confirm it is retained and populated in the second page
        """
        self.settings["REWRITE"] = False
        self.settings["URL_SPECIFIC"] = False
        self.settings["CLIENT_ID"] = False
        response = self.browser.get("/index.html")
        session, session_id = self.get_session(response)
        session_key = session.session_key
        self.assertTrue("classview" in session.keys())
        self.assertFalse(session["created_cookieless"])
        # Post form to second page
        postdict = {self.skey: session_id}
        response = self.browser.post("/function-view.html", postdict)
        # Get session again
        session, session_id = self.get_session(response)
        self.assertTrue("funcview" in session.keys())
        self.assertEqual(session.session_key, session_key)

    def test_session_not_retained_other_url(self):
        """ Get the first page then retrieve the session
            and confirm it is no longer retained if the url is not maintained
        """
        self.settings["REWRITE"] = False
        self.settings["URL_SPECIFIC"] = True
        self.settings["CLIENT_ID"] = False
        url = "/index.html"
        response = self.browser.get(url)
        session, session_id = self.get_session(response, url)
        start_session_key = session.session_key
        self.assertNotEqual(session.keys(), [])
        self.assertTrue("classview" in session.keys())
        postdict = {self.skey: session_id}
        # Post form to second page where session is restarted
        url = "/function-view.html"
        response = self.browser.post(url, postdict)
        session, session_id = self.get_session(response, url)
        self.assertTrue("funcview" in session.keys())
        self.assertNotEqual(session.session_key, start_session_key)
        # Post form back to first page where session is retained
        # NOTE: cannot post back to "/" need a named page or posts are rejected
        url = "/index.html"
        response = self.browser.post(url, postdict)
        session, session_id = self.get_session(response, url)
        self.assertFalse(session.get("created_cookieless", False))
        self.assertEqual(session.session_key, start_session_key)

    def test_session_not_retained_other_host(self):
        """ Get the first page then retrieve the session
            and confirm it is no longer retained if the host changes
        """
        self.settings["REWRITE"] = False
        self.settings["URL_SPECIFIC"] = True
        self.settings["CLIENT_ID"] = False
        url = "/index.html"
        response = self.browser.get(url)
        session, session_id = self.get_session(response, url)
        start_session_key = session.session_key
        self.assertTrue("classview" in session.keys())
        postdict = {self.skey: session_id}
        # Post form back to first page where server has changed
        response = self.browser.post(
            url, postdict, SERVER_NAME="www.othertestserver.org"
        )
        session, session_id = self.get_session(response, url)
        self.assertNotEqual(session.session_key, start_session_key)
        # Post form back to first page where host is the same
        response = self.browser.post(url, postdict)
        session, session_id = self.get_session(response, url)
        self.assertFalse(session.get("created_cookieless", False))
        self.assertEqual(session.session_key, start_session_key)

    def test_session_not_retained_other_client(self):
        """ Get the first page then retrieve the session
            and confirm it is no longer retained if the client changes
        """
        self.settings["REWRITE"] = False
        self.settings["URL_SPECIFIC"] = False
        self.settings["CLIENT_ID"] = True
        url = "/index.html"
        agent = "unknown browser"
        response = self.browser.get(url, HTTP_USER_AGENT=agent)
        session, session_id = self.get_session(response, url, agent)
        start_session_key = session.session_key
        self.assertTrue("classview" in session.keys())
        postdict = {self.skey: session_id}
        # Post form back to first page where client has changed
        response = self.browser.post(url, postdict, HTTP_USER_AGENT="othertestclient")
        session, session_id = self.get_session(response, url, agent)
        self.assertNotEqual(session.session_key, start_session_key)
        # Post form back to first page where session client stays the same
        response = self.browser.post(url, postdict)
        session, session_id = self.get_session(response, url, agent)
        self.assertFalse(session.get("created_cookieless", False))
        self.assertEqual(session.session_key, start_session_key)

    def test_breach_mitigation(self):
        """
        Check that compression of repeated requests leads to differing string lengths
        """
        self.settings["REWRITE"] = True
        self.settings["USE_GET"] = True
        url = "/plain-view.html"
        response = self.browser.get(url)

        search_str = r'"/\?' + settings.SESSION_COOKIE_NAME + '=(.*?)"'

        m = re.search(search_str, response.content.decode())
        session_key = m.group(1)
        params = {settings.SESSION_COOKIE_NAME: session_key}

        array = [
            len(self._compress(self.browser.get(url, params).content))
            for x in range(100)
        ]
        self.assertTrue(
            len(set(array)) > 1,
            "assert that the length of subsequent requests when compressed have a different length",
        )

    def _compress(self, string):
        contents = BytesIO()
        gzfile = GzipFile(fileobj=contents, mode="wb")
        gzfile.write(string)
        gzfile.close()
        return contents.getvalue()

    def test_content_length(self):
        """Check that content length is set correctly"""
        self.settings["REWRITE"] = True
        self.settings["USE_GET"] = True
        response = self.browser.get("/plain-view.html")
        url = "?%s=" % self.skey
        # Check content is encoded
        self.assertEqual(type(response.content), bytes)
        self.assertTrue(url in response.content.decode())
        # Check length is set correctly
        self.assertEqual(len(response.content.decode()), int(response["Content-Length"]))
