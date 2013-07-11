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

from tailbone import DEBUG

import json
import logging
import random
import webapp2

from google.appengine.api import channel
from google.appengine.ext import ndb

class ConnectedHandler(BaseHandler):
  @as_json
  def post(self):
    client_id = self.request.get('from')
    try:
      client_id = int(client_id)
    except:
      pass
    logging.info("Connecting client id {}".format(client_id))


class DisconnectedHandler(BaseHandler):
  @as_json
  def post(self):
    client_id = self.request.get('from')
    try:
      client_id = int(client_id)
    except:
      pass
    logging.info("Disconnecting client id {}".format(client_id))
    unbind(client_id)


class ChannelHandler(BaseHandler):
  @as_json
  def get(self, name):
    # TODO(doug): add better client_id generation
    data = parse_body(self)
    method = data.get("method")
    client_id = data.get("client_id")
    if method == "token":
      return {"token": channel.create_channel(str(client_id))}
    elif method == "bind":
      bind(client_id, data.get("name"))
    elif method == "unbind":
      unbind(client_id, data.get("name"))
    elif method == "trigger":
      trigger(data.get("name"), data.get("payload"))


EXPORTED_JAVASCRIPT = compile_js([
  "tailbone/channel/channel.js",
], ["Channel"])


app = webapp2.WSGIApplication([
  (r"{}channel/.*".format(PREFIX), ChannelHandler),
  ], debug=DEBUG)


connected = webapp2.WSGIApplication([
  ("/_ah/channel/connected/", ConnectedHandler),
  ("/_ah/channel/disconnected/", DisconnectedHandler),
  ], debug=DEBUG)