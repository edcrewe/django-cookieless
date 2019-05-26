""" Obscure the session id when passing it around in HTML """
import string
import base64
import hashlib

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
        self.settings = getattr(settings, "COOKIELESS", DEFAULT_SETTINGS)
        self.cipher = Fernet(CIPHER_KEY)

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

        hashit = self.check_specific(request)
        session_key = self.cipher.encrypt(bytes(sessionid, "utf8"))
        return hashit + session_key.decode()

    def decrypt(self, request, sessionid):
        """ Avoid showing plain sessionids
            Optionally require that a referer exists and matches the
            whitelist, or reset the session
        """
        if not sessionid:
            return ""

        sessionid = bytes(sessionid, "utf-8")
        hashit = self.check_specific(request)
        if hashit and not sessionid.decode().startswith(hashit):
            return ""
        sessionid = sessionid[len(hashit) :]
        if self.settings.get("HOSTS", []):
            referer = request.META.get("HTTP_REFERER", "None")
            if referer == "None":
                # End session unless a referer is passed
                return ""
            url = parse(referer)
            if url.hostname not in self.settings["HOSTS"]:
                err = "%s is unauthorised" % url.hostname
                raise Exception(err)
        cipher = Fernet(CIPHER_KEY)
        session_key = cipher.decrypt(sessionid)
        try:
            return session_key.decode()
        except:
            return ""

    def key_tuple(self, request):
        """ For use in generated html """
        return (
            settings.SESSION_COOKIE_NAME,
            self.encrypt(request, request.session.session_key),
        )

    def check_specific(self, request):
        """ optionally make secret client or url dependent
            NB: Needs to be 32 characters base64 encoded to be Fernet secret
        """
        specific = ""
        if self.settings.get("URL_SPECIFIC", False):
            specific += request.META.get("SERVER_NAME", "")
            specific += request.META.get("PATH_INFO", "")
        if self.settings.get("CLIENT_ID", False):
            specific += request.META.get("REMOTE_ADDR", "127.0.0.1")
            specific += request.META.get("HTTP_USER_AGENT", "unknown browser")
        if specific:
            return hashlib.md5(specific.encode()).hexdigest()
        return ""
