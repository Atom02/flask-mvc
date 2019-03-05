from werkzeug.routing import RoutingException, HTTPException
from flask import redirect,request
import urllib
class RequestRedirect(HTTPException, RoutingException):
    """Raise if the map requests a redirect. This is for example the case if
    `strict_slashes` are activated and an url that requires a trailing slash.
    The attribute `new_url` contains the absolute destination url.
    The attribute `code` is returned status code.
    """
    def __init__(self, new_url, code=301):
        RoutingException.__init__(self, new_url)
        self.new_url = new_url
        self.code = code
        print(request.endpoint)
    def get_response(self, environ):
        added = {"next":request.endpoint}
        encoded = urllib.parse.urlencode(added)
        if "?" in self.new_url:
            goTo = self.new_url+"&"+encoded
        else:
            goTo = self.new_url+"?"+encoded
        return redirect(goTo, code = self.code)