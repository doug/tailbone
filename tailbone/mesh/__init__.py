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

# shared resources and global variables
from tailbone import as_json, BaseHandler, compile_js, AppError
from tailbone import config
from tailbone import DEBUG
from tailbone import PREFIX
from tailbone.compute_engine import LoadBalancer
from tailbone.compute_engine import TailboneCEInstance
from tailbone.compute_engine import websocket
from tailbone.compute_engine import turn

import base64
import json
import os
import random
import string
import webapp2

from google.appengine.api import users
from google.appengine.api import memcache
from google.appengine.api import app_identity
from google.appengine.api import lib_config 

class _ConfigDefaults(object):
  ROOM_EXPIRATION = 86400  # one day in seconds
  ENABLE_WEBSOCKET = False
  ENABLE_TURN = False

  def generate_room_name():
    return generate_word() + "." + generate_word()


_config = lib_config.register('tailbone_mesh', _ConfigDefaults.__dict__)

def room_hash(name):
  return "tailbone-mesh-room-{}".format(base64.b64encode(name))

def unique_name():
  name = _config.generate_room_name()
  room = room_hash(name)
  address = memcache.get(room)
  if address:
    return unique_name()
  return name, room, address

def get_or_create_room(request, name=None):
  if not name:
    name, room, address = unique_name()
  else:
    room = room_hash(name)
    address = memcache.get(room)
  if not address:
    if _config.ENABLE_WEBSOCKET:
      if DEBUG:
        class DebugInstance(object):
          address = request.remote_addr if str(request.remote_addr) != "::1" else "localhost"
        instance = DebugInstance()
      else:
        instance = LoadBalancer.find(websocket.TailboneWebsocketInstance, request)
      if not instance:
        raise AppError('Instance not yet ready, try again later.')
      address = "ws://{}:{}/{}".format(instance.address, websocket.WEBSOCKET_PORT, name)
    else:
      address = '/api/channel/'
    memcache.set(room, address, time=_config.ROOM_EXPIRATION)
  return name, address


class MeshHandler(BaseHandler):
  @as_json
  def get(self, name):
    room, ws = get_or_create_room(self.request, name)
    # ts = LoadBalancer.find(turn.TailboneTurnInstance, self.request)
    username = self.request.get("username", generate_word())
    username, password = turn.credentials(username)
    ts = None
    # ts = "turn:173.255.117.180"
    return {
      "ws": ws,
      "name": room,
      "turn": ts,
      "username": username,
      "password": password,
    }

  @as_json
  def delete(self, name):
    if not config.is_current_user_admin():
      raise AppError("Unauthorized.")
    if not name:
      raise AppError("Must provide name.")

EXPORTED_JAVASCRIPT = compile_js([
  "tailbone/mesh/js/msgpack.js",
  "tailbone/mesh/js/EventDispatcher.js",
  "tailbone/mesh/js/StateDrive.js",
  "tailbone/mesh/js/Channel.js",
  "tailbone/mesh/js/ChannelChannel.js",
  "tailbone/mesh/js/ChannelMultiplexer.js",
  "tailbone/mesh/js/SocketChannel.js",
  "tailbone/mesh/js/SocketMultiplexer.js",
  "tailbone/mesh/js/NetChannel.js",
  "tailbone/mesh/js/RTCChannel.js",
  "tailbone/mesh/js/Node.js",
  "tailbone/mesh/js/Peers.js",
  "tailbone/mesh/js/Mesh.js",
], ["Mesh"])

app = webapp2.WSGIApplication([
  (r"{}mesh/?(.*)".format(PREFIX), MeshHandler),
], debug=DEBUG)


# Gibberish generator modified from: https://github.com/greghaskins/gibberish
VOWELS = "aeiou"
INITIAL_CONSONANTS = list(set(string.ascii_lowercase) - set(VOWELS)
                      - set("qxc")
                      | set(["bl", "br", "cl", "cr", "dr", "fl",
                            "fr", "gl", "gr", "pl", "pr", "sk",
                            "sl", "sm", "sn", "sp", "st", "str",
                            "sw", "tr", "ch", "sh"])
                         )
FINAL_CONSONANTS = list(set(string.ascii_lowercase) - set(VOWELS)
                    - set("qxcsj")
                    | set(["ct", "ft", "mp", "nd", "ng", "nk", "nt",
                           "pt", "sk", "sp", "ss", "st", "ch", "sh"])
                       )


def generate_word():
    """Returns a random consonant-vowel-consonant pseudo-word."""
    return ''.join(random.choice(s) for s in (INITIAL_CONSONANTS,
                                              VOWELS,
                                              FINAL_CONSONANTS))