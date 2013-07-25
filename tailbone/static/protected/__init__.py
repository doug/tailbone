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


class ProtectedHandler(webapp2.RequestHandler):
  def proxy(self, *args, **kwargs):
    is_admin = config.is_current_user_admin()
    if not is_admin:
      self.response.out.write("""
<html><head></head><body>
You must be an approved logged in user.
<a href="/api/login?continue={}">Login In</a>
</body></html>
""".format(self.request.path))
      self.error(401)
      return
    path = self.request.path
    path = "client/app" + path
    if path[-1] == "/":
      path += "index.html"
    mimetype, _ = mimetypes.guess_type(path)
    self.response.headers["Content-Type"] = mimetype
    with open(path) as f:
      self.response.out.write(f.read())
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

