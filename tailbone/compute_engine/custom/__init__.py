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
from tailbone.compute_engine import STARTUP_SCRIPT_BASE

import binascii
from hashlib import sha1
import hmac
import md5
import time
import webapp2

from google.appengine.api import lib_config



class _ConfigDefaults(object):

  STARTUP_SCRIPT = """
echo "You should edit the appengine_config.py file with your own startup_script."
"""

  def calc_load(stats):
    return TailboneCEInstance.calc_load(stats)


_config = lib_config.register('tailbone_compute_engine_custom', _ConfigDefaults.__dict__)

# Prefixing internal models with Tailbone to avoid clobbering when using RESTful API
class TailboneCustomInstance(TailboneCEInstance):
  PARAMS = dict(TailboneCEInstance.PARAMS, **{
    "name": "custom-id",
    "metadata": {
      "items": [
        {
          "key": "startup-script",
          "value": STARTUP_SCRIPT_BASE + _config.STARTUP_SCRIPT,
        },
      ],
    }
  })

  @staticmethod
  def calc_load(stats):
    return _config.calc_load(stats)


class CustomHandler(BaseHandler):
  @as_json
  def get(self):
    return {
      "ip": address
    }

app = webapp2.WSGIApplication([
  (r"{}custom/?.*".format(PREFIX), CustomHandler),
], debug=DEBUG)