""" Constants for cookieless """
LINKS_RE = r'<a(?P<pre_href>[^>]*?)href=["\'](?P<in_href>[^"\']*?)(?P<anchor>#\S+)?["\'](?P<post_href>[^>]*?)>'

DEFAULT_SETTINGS = {
    "REWRITE": True,
    "USE_GET": True,
    "CLIENT_ID": True,
    "HOSTS": [],
    "NO_COOKIE_PERSIST": True,
    "URL_SPECIFIC": False,
    "DELETE_COOKIES": False,
}
