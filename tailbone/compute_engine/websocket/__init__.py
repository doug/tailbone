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

from tailbone import as_json
from tailbone import BaseHandler
from tailbone import DEBUG
from tailbone import PREFIX
from tailbone.compute_engine import LoadBalancer
from tailbone.compute_engine import TailboneCEInstance

import webapp2

WEBSOCKET_PORT = 2345

# TODO: Use an image instead of a startup-script for downloading dependencies

# Prefixing internal models with Tailbone to avoid clobbering when using RESTful API
class TailboneWebsocketInstance(TailboneCEInstance):
  PARAMS = dict(TailboneCEInstance.PARAMS, **{
    "name": "websocket-id",
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
curl -O https://raw.github.com/doug/tailbone/reorg/tailbone/compute_engine/load_reporter.py
python load_reporter.py &

# websocket server
curl -O https://pypi.python.org/packages/source/t/tornado/tornado-3.0.1.tar.gz
tar xvfz tornado-3.0.1.tar.gz
cd tornado-3.0.1
python setup.py install
cd ..
rm -rf tornado-3.0.1
rm tornado-3.0.1.tar.gz
curl -O https://raw.github.com/doug/tailbone/reorg/tailbone/compute_engine/websocket/websocket.py
python websocket.py 

""",
        },
      ],
    }
  })

class WebsocketHandler(BaseHandler):
  @as_json
  def get(self):
    instance = LoadBalancer.find(TailboneWebsocketInstance, self.request)
    return {
      "ws": "ws://{}:{}".format(instance.address, WEBSOCKET_PORT)
    }


app = webapp2.WSGIApplication([
  (r"{}compute_engine/websocket/.*".format(PREFIX), WebsocketHandler),
  ], debug=DEBUG)

