""" Obscure the session id when passing it around in HTML """
import string
import random

from django.conf import settings
from urllib import parse
from cryptography.fernet import Fernet
from cookieless.config import DEFAULT_SETTINGS

CIPHER_KEY = Fernet.generate_key()


class CryptSession(object):
    """ Tool to generate encrypted session id for
        middleware or templatetags
    """

    def __init__(self):
        self.secret = CIPHER_KEY
        self.settings = getattr(settings, "COOKIELESS", DEFAULT_SETTINGS)

    def prepare_url(self, url):
        patt = None
        if url.find("?") == -1:
            patt = "%s?"
        else:
            patt = "%s&amp;"
        return patt % (url,)

    def encrypt(self, request, sessionid):
        """ Avoid showing plain sessionids
            Use base64 - but strip the line return it adds
        """
        if not sessionid:
            return ""

        secret = self._secret(request)
        cipher = Fernet(secret)
        session_key = cipher.encrypt(bytes(sessionid, "utf8"))
        return session_key.decode()

    def decrypt(self, request, sessionid):
        """ Avoid showing plain sessionids
            Optionally require that a referer exists and matches the
            whitelist, or reset the session
        """
        if not sessionid:
            return ""

        sessionid = bytes(sessionid, "utf-8")

        secret = self._secret(request)
        if self.settings.get("HOSTS", []):
            referer = request.META.get("HTTP_REFERER", "None")
            if referer == "None":
                # End session unless a referer is passed
                return ""
            url = parse(referer)
            if url.hostname not in self.settings["HOSTS"]:
                err = "%s is unauthorised" % url.hostname
                raise Exception(err)
        cipher = Fernet(secret)
        session_key = cipher.decrypt(sessionid)
        try:
            return str(session_key, "utf8")
        except:
            return ""

    def key_tuple(self, request):
        """ For use in generated html """
        return (
            settings.SESSION_COOKIE_NAME,
            self.encrypt(request, request.session.session_key),
        )

    def _secret(self, request):
        """ optionally make secret client or url dependent
            NB: Needs to be at least 16 characters so add secret to META data
        """
        secret = self.secret
        specific = ""
        return secret
        if self.settings.get("URL_SPECIFIC", False):
            specific += request.META.get("SERVER_NAME", "")
            specific += request.META.get("PATH_INFO", "")
        if self.settings.get("CLIENT_ID", False):
            specific += request.META.get("REMOTE_ADDR", "127.0.0.1")
            specific += request.META.get("HTTP_USER_AGENT", "unknown browser")
        if specific:
            cipher = Fernet(self.secret)
            secret = cipher.encrypt(bytes(specific, "utf8") + self.secret)
            # new_secret = secret.decode("ascii")
            # secret = new_secret[:16]
        return secret

    def xor(self, s1, s2):
        """if s1 and s2 are not the same length, pad the smaller one"""
        if len(s2) < len(s1):
            (s1, s2) = (s2, s1)
        if len(s1) < len(s2):
            s1 = s1 * ((len(s2) / len(s1)) + 1)
        return "".join(chr(ord(a) ^ ord(b)) for a, b in zip(s1, s2))

    def _random_string_generator(self, length):
        return "".join(
            random.choice(string.ascii_letters + string.digits) for x in range(length)
        )
