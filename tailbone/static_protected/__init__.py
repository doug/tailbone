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

from tailbone import config

import os
import mimetypes
import urllib
import webapp2

from google.appengine.api import lib_config

_config = lib_config.register("protected", {"PASSWORD": "notasecret",
                                            "BASE_PATH": "client/app"})
PROTECTED_PATH = "{}protected".format(config.PREFIX)


class ProtectedHandler(webapp2.RequestHandler):
  def get(self, *args, **kwargs):
    p = self.request.path
    password = self.request.cookies.get("whisper")
    if password != _config.PASSWORD:
      self.redirect(PROTECTED_PATH+"?continue="+p)
      return
    p = _config.BASE_PATH + p
    if p[-1] == "/":
      p += "index.html"
    mime, encoding = mimetypes.guess_type(p)
    self.response.headers["Content-Type"] = mime or "text/html"
    try:
      with open(urllib.unquote(p), "r") as f:
        self.response.out.write(f.read())
    except IOError:
      self.error(404)


class AuthHandler(webapp2.RequestHandler):
  def get(self):
    self.response.out.write("""
<html>
<head>
<script>
  function getParameterByName(name) {
      name = name.replace(/[\[]/, "\\\[").replace(/[\]]/, "\\\]");
      var regex = new RegExp("[\\?&]" + name + "=([^&#]*)"),
          results = regex.exec(location.search);
      return results == null ? "" : decodeURIComponent(results[1].replace(/\+/g, " "));
  }
  var password = prompt("Password:");
  if (password != "") {
    var cookie = "whisper="+escape(password)+";"
    cookie += " path=/;";
    document.cookie = cookie;
    var href = window.location.href;
    window.location.href = getParameterByName("continue");
  }
</script>
</head>
<body>
</body>
</html>
""")

app = webapp2.WSGIApplication([
  (PROTECTED_PATH, AuthHandler),
  (r".*", ProtectedHandler),
], debug=config.DEBUG)
