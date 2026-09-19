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

    def test_redirect_rewrite_same_host(self):
        """Rewrite same-host redirects to carry the encrypted session token."""
        self.settings["REWRITE"] = True
        self.settings["USE_GET"] = True
        self.settings["URL_SPECIFIC"] = False
        self.settings["CLIENT_ID"] = False
        response = self.browser.get("/redirect-same-host.html", SERVER_NAME="localhost")
        self.assertEqual(response.status_code, 302)
        self.assertTrue("http://localhost/index.html?" in response["Location"])
        self.assertTrue(f"{self.skey}=" in response["Location"])

    def test_redirect_not_rewritten_other_host(self):
        """Do not rewrite redirects to a different host."""
        self.settings["REWRITE"] = True
        self.settings["USE_GET"] = True
        response = self.browser.get("/redirect-other-host.html", SERVER_NAME="localhost")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], "http://example.org/index.html")

    def test_standard_session_cookie_set_for_undecorated_view(self):
        """Undecorated views should still use standard cookie sessions."""
        response = self.browser.get("/cookie-view.html", SERVER_NAME="localhost")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.skey in response.cookies)
        self.assertTrue(self.skey in self.browser.cookies)

    def test_no_cookie_persist_rotates_cookie_backed_session(self):
        """No-cookie views should rotate away from cookie-backed sessions."""
        self.settings["REWRITE"] = True
        self.settings["USE_GET"] = True
        self.settings["NO_COOKIE_PERSIST"] = True
        self.settings["URL_SPECIFIC"] = False
        self.settings["CLIENT_ID"] = False
        self.settings["HOSTS"] = []

        self.browser.get("/cookie-view.html", SERVER_NAME="localhost")
        cookie_key = self.browser.cookies[self.skey].value
        token = self.crypt_sesh.encrypt(self.factory.get("/plain-view.html"), cookie_key)

        response = self.browser.post(
            "/plain-view.html",
            {self.skey: token},
            SERVER_NAME="localhost",
            HTTP_COOKIE=f"{self.skey}={cookie_key}",
        )
        session, _session_id = self.get_session(response, "/plain-view.html")
        old_session = self.engine.SessionStore(cookie_key)

        self.assertNotEqual(session.session_key, cookie_key)
        self.assertTrue(session.get("no_cookies", False))
        self.assertEqual(old_session.get("cookieview", ""), "my_cookie_view")

    def test_delete_cookies_expires_incoming_cookies(self):
        """Delete-cookies mode should issue expiry cookies for incoming values."""
        self.settings["REWRITE"] = True
        self.settings["USE_GET"] = True
        self.settings["DELETE_COOKIES"] = True
        self.settings["NO_COOKIE_PERSIST"] = False
        self.settings["URL_SPECIFIC"] = False
        self.settings["CLIENT_ID"] = False

        self.browser.get("/cookie-view.html", SERVER_NAME="localhost")
        cookie_key = self.browser.cookies[self.skey].value
        self.browser.cookies["legacycookie"] = "legacy-value"
        token = self.crypt_sesh.encrypt(self.factory.get("/plain-view.html"), cookie_key)

        response = self.browser.post(
            "/plain-view.html",
            {self.skey: token},
            SERVER_NAME="localhost",
            HTTP_COOKIE=f"{self.skey}={cookie_key}; legacycookie=legacy-value",
        )

        self.assertTrue(self.skey in response.cookies)
        self.assertTrue("legacycookie" in response.cookies)
        self.assertEqual(str(response.cookies[self.skey]["max-age"]), "0")
        self.assertEqual(str(response.cookies["legacycookie"]["max-age"]), "0")

    def test_binary_response_not_rewritten_and_length_correct(self):
        """Binary responses should not crash rewrite logic or be mutated."""
        self.settings["REWRITE"] = True
        self.settings["USE_GET"] = True

        response = self.browser.get("/binary-view.bin", SERVER_NAME="localhost")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.content,
            b"\xff\xfe\xfd\x00binary-cookieless-data",
        )
        self.assertEqual(int(response["Content-Length"]), len(response.content))

    def test_link_rewrite_preserves_anchor_and_existing_query(self):
        """Link rewrite should add session id while preserving query/anchor parts."""
        self.settings["REWRITE"] = True
        self.settings["USE_GET"] = True
        self.settings["URL_SPECIFIC"] = False
        self.settings["CLIENT_ID"] = False

        response = self.browser.get("/link-view.html", SERVER_NAME="localhost")
        body = response.content.decode()

        self.assertTrue(
            re.search(r'href="/function-view.html\?%s=[^"#]+#frag"' % self.skey, body)
        )
        self.assertTrue(
            re.search(
                r'href="/function-view.html\?foo=bar&amp;%s=[^"#]+#frag2"'
                % self.skey,
                body,
            )
        )
        self.assertTrue(
            re.search(
                r'href="https://localhost/index.html\?%s=[^"#]+"' % self.skey,
                body,
            )
        )
        self.assertTrue(
            re.search(
                r'href="//localhost/function-view.html\?%s=[^"#]+"' % self.skey,
                body,
            )
        )
        self.assertTrue('href="https://www.dr-chuck.com/"' in body)
        self.assertTrue('href="//www.dr-chuck.com/example"' in body)
        self.assertTrue('href="#page-anchor"' in body)
        self.assertTrue('href="javascript:void(0)"' in body)
        self.assertTrue('data-href="/not-a-link"' in body)
        self.assertTrue('<span href="/not-rewritten">' in body)
