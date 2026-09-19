""" Obscure the session id when passing it around in HTML """
import base64
import hashlib

from django.conf import settings
from urllib import parse
from cryptography.fernet import Fernet
from cookieless.config import DEFAULT_SETTINGS


def _as_bytes(value):
    if isinstance(value, bytes):
        return value
    return str(value).encode("utf-8")


def _derived_fernet_key(secret_material):
    digest = hashlib.sha256(_as_bytes(secret_material)).digest()
    return base64.urlsafe_b64encode(digest)


def get_cipher_key(cookieless_settings=None):
    """Return a stable fernet key from settings.

    - If COOKIELESS['CIPHER_KEY'] is a valid fernet key, use it directly.
    - If COOKIELESS['CIPHER_KEY'] is set but not fernet-formatted, derive one.
    - Otherwise derive a key from Django SECRET_KEY.
    """
    current_settings = cookieless_settings or getattr(settings, "COOKIELESS", {})
    configured_key = current_settings.get("CIPHER_KEY")

    if configured_key:
        key_bytes = _as_bytes(configured_key)
        try:
            Fernet(key_bytes)
            return key_bytes
        except (TypeError, ValueError):
            return _derived_fernet_key(key_bytes)

    return _derived_fernet_key(settings.SECRET_KEY)


class CryptSession:
    """ Tool to generate encrypted session id for
        middleware or templatetags
    """

    def __init__(self):
        self.settings = getattr(settings, "COOKIELESS", DEFAULT_SETTINGS)
        self.cipher_key = get_cipher_key(self.settings)
        self.cipher = Fernet(self.cipher_key)

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
            url = parse.urlparse(referer)
            if url.hostname not in self.settings["HOSTS"]:
                err = "%s is unauthorised" % url.hostname
                raise Exception(err)
        session_key = self.cipher.decrypt(sessionid)
        try:
            return session_key.decode()
        except UnicodeDecodeError:
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
