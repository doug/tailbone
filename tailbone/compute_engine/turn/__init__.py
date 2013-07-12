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

from tailbone import BaseHandler
from tailbone import as_json
from tailbone import config
from tailbone import DEBUG
from tailbone import PREFIX
from tailbone.compute_engine import TailboneCEInstance

import binascii
from hashlib import sha1
import hmac
import md5
import time
import webapp2

from google.appengine.api import lib_config

_config = lib_config.register("tailbone_turn", {
                              "SECRET": "notasecret",
                              "RESTRICTED_DOMAINS": ["localhost"],
                              })

# Prefixing internal models with Tailbone to avoid clobbering when using RESTful API
class TailboneTurnInstance(TailboneCEInstance):
  PARAMS = dict(TailboneCEInstance.PARAMS, **{
    "name": "turn-id",
    "metadata": {
      "items": [
        {
          "key": "startup-script",
          "value": """#!/bin/bash

# install deps
apt-get install -y build-essential python-dev

# load reporter
curl -O http://psutil.googlecode.com/files/psutil-0.6.1.tar.gz
tar xvfz psutil-0.6.1.tar.gz
cd psutil-0.6.1
python setup.py install
cd ..
rm -rf psutil-0.6.1
rm psutil-0.6.1.tar.gz
curl -O https://raw.github.com/dataarts/tailbone/mesh/tailbone/compute_engine/load_reporter.py
python load_reporter.py &

# load turnserver
curl -O http://rfc5766-turn-server.googlecode.com/files/turnserver-1.8.7.0-binary-linux-wheezy-ubuntu-mint-x86-64bits.tar.gz
tar xvfz turnserver-1.8.7.0-binary-linux-wheezy-ubuntu-mint-x86-64bits.tar.gz
dpkg -i rfc5766-turn-server_1.8.7.0-1_amd64.deb
apt-get -f install
turnserver --use-auth-secret -v -a -X -f --static-auth-secret notasecret -r localhost -r appspot.com
 
""",
        },
      ],
    }
  })


def credentials(username):
  timestamp = str(time.mktime(time.gmtime())).split('.')[0]
  username = "{}:{}".format(username, timestamp)
  password = hmac.new(_config.SECRET, username, sha1)
  password = binascii.b2a_base64(password.digest())[:-1]
  return username, password


class TurnHandler(BaseHandler):
  @as_json
  def get(self):
    username = self.request.get("username")
    if not username:
      raise AppError("Must provide username.")
    username, password = credentials(username)
    return {
      "username": username,
      "password": password,
      "turn": "some address"
    }

app = webapp2.WSGIApplication([
  (r"{}turn/?.*".format(PREFIX), TurnHandler),
], debug=DEBUG)