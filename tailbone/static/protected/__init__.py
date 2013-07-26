# Copyright 2013 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import urllib
import mimetypes
import webapp2
from tailbone import DEBUG
from tailbone import config

from google.appengine.api import urlfetch
from google.appengine.api import lib_config

# Example of admin auth
class _ConfigDefaults(object):
  def is_authorized(request):
    return config.is_current_user_admin()

  def unauthorized_response(request):
    return """
<html><head></head><body>
You must be an approved logged in user.
<a href="/api/login?continue=%s">Login In</a>
</body></html>
""" % (request.path,)

# Example of password auth
class _ConfigDefaults(object):
  PASSWORD = "notasecret"

  def is_authorized(request):
    return _config.PASSWORD == request.cookies.get("whisper")

  def unauthorized_response(request):
    return """
<html><head>
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no" />
<script>
  function proceed() {
    var password = document.getElementById("pass").value;
    if (password != "") {
      var cookie = "whisper="+escape(password)+";"
      cookie += " path=/;";
      document.cookie = cookie;
    }
  }
</script>
</head><body>
You must be an approved logged in user.
  <p>Authentication:</p>
  <form onsubmit="proceed()" action="%s">
    <input type="password" id="pass" />
    <input type="submit" value="Enter" />
  </form>
</body></html>
""" % (request.path,)

_config = lib_config.register('tailbone_static_protected', _ConfigDefaults.__dict__)

class ProtectedHandler(webapp2.RequestHandler):
  def proxy(self, *args, **kwargs):
    authorized = _config.is_authorized(self.request)
    if not authorized:
      self.response.out.write(
        _config.unauthorized_response(self.request))
      return
    path = self.request.path
    path = "client/app" + path
    if path[-1] == "/":
      path += "index.html"
    mimetype, _ = mimetypes.guess_type(path)
    self.response.headers["Content-Type"] = mimetype
    try:
      with open(urllib.unquote(path)) as f:
        self.response.out.write(f.read())
    except IOError:
      self.error(404)
  def get(self, *args, **kwargs):
    self.proxy(*args, **kwargs)
  def put(self, *args, **kwargs):
    self.proxy(*args, **kwargs)
  def post(self, *args, **kwargs):
    self.proxy(*args, **kwargs)
  def delete(self, *args, **kwargs):
    self.proxy(*args, **kwargs)


app = webapp2.WSGIApplication([
  (r".*", ProtectedHandler),
  ], debug=DEBUG)
