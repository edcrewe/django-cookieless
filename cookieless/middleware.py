#-*- coding:utf-8 -*-
from django.http  import  HttpResponseRedirect
import re, pdb

class CookielessSessionMiddleware(object):
    """ Django snippets julio carlos and Ivscar 
        http://djangosnippets.org/snippets/1540/
    """
    def __init__(self):

        self._re_links = re.compile(r'<a(?P<pre_href>[^>]*?)href=["\'](?P<in_href>[^"\']*?)(?P<anchor>#\S+)?["\'](?P<post_href>[^>]*?)>', re.I)
        self._re_forms = re.compile('</form>', re.I)

    def _prepare_url(self, url):
        patt = None
        if url.find('?') == -1:
            patt = '%s?'
        else:
            patt = '%s&amp;'
        return patt % (url,)

    def process_request(self, request):
        if not request.COOKIES.has_key('sessionid'):
            value = None
            if hasattr(request, 'POST') and request.POST.has_key('sessionid'):
                value = request.POST['sessionid']
            elif hasattr(request, 'GET') and request.GET.has_key('sessionid'):
                value = request.GET['sessionid']
            if value:
                request.COOKIES['sessionid'] = value        

    def process_response(self, request, response):

        if not request.path.startswith("/admin")  and response.cookies.has_key('sessionid'):
            try:
                sessionid = response.cookies['sessionid'].coded_value
                if type(response) is HttpResponseRedirect:
                    if not sessionid: 
                        sessionid = ""
                    redirect_url = [x[1] for x in response.items() if x[0] == "Location"][0]
                    redirect_url = self._prepare_url(redirect_url)
                    return HttpResponseRedirect('%ssessionid=%s' % (redirect_url,sessionid,)) 


                def new_url(m):
                    anchor_value = ""
                    if m.groupdict().get("anchor"): 
                        anchor_value = m.groupdict().get("anchor")
                    return_str = '<a%shref="%ssessionid=%s%s"%s>' % (
                                     m.groupdict()['pre_href'],
                                     self._prepare_url(m.groupdict()['in_href']),
                                     sessionid,
                                     anchor_value,
                                     m.groupdict()['post_href']
                                     )
                    return return_str                                 
                response.content = self._re_links.sub(new_url, response.content)


                repl_form = '''<div><input type="hidden" name="sessionid" value="%s" />
                               </div></form>'''
                repl_form = repl_form % (sessionid,)
                response.content = self._re_forms.sub(repl_form, response.content)

                return response
            except:

                return response
        else:
            return response        
