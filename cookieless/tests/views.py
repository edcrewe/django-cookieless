# Create your views here.

from django.views.generic import TemplateView
from django.http import HttpResponse
import datetime

def my_function_view(request):
    request.session['funcview'] = 'my_function_view'
    html = "<html><body><h1>Function view</h1>"
    html += '<p><a href="/">Class view</a></p><hr />'
    html += "My session %s.<ul>" % request.session.session_key
    for key, value in request.session.items():
        html += "<li>%s = %s </li>" % (key, value)
    html += '<ul></body></html>'    
    return HttpResponse(html)


class MyClassView(TemplateView):
    template_name = "classview.html"

    def dispatch(self, *args, **kwargs):
        args[0].session['classview'] = 'MyClassView'
        now = datetime.datetime.now()
        args[0].session[now] = 'more stuff'
        return super(MyClassView, self).dispatch(*args, **kwargs)
    

