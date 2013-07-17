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


## Edit the code below to add you own hooks and modify tailbone's behavior

## Base Tailbone overrides and hooks

## Set the global default namespace
# def namespace_manager_default_namespace_for_request():
#   return "my_custom_namespace"

## Use JSONP for all apis
# tailbone_JSONP = False

## modify the below functions to change how users are identified
# tailbone_is_current_user_admin = 
# tailbone_get_current_user = 
# tailbone_create_login_url = 
# tailbone_create_logout_url = 

## Use cloud store instead of blobstore
# tailbone_files_CLOUDSTORE = False

## Store counts for restful models accessible in HEAD query
# tailbone_restful_METADATA = False

## If specified is a list of tailbone.restful.ScopedModel objects these will be the only ones allowed.
## This is a next level step of model restriction to your db, this replaces validation.json
# from google.appengine.ext import ndb
# from tailbone.restful import ScopedModel
# class MyModel(ScopedModel):
#   stuff = ndb.IntegerProperty()
# tailbone_restful_DEFINED_MODELS = {"mymodel": MyModel}
# tailbone_restful_RESTRICT_TO_DEFINED_MODELS = False

## Protected model names gets overridden by RESTRICTED_MODELS
# tailbone_restful_PROTECTED_MODEL_NAMES = ["(?i)tailbone.*", "custom", "(?i)users"]

## Proxy can only be used for the restricted domains if specified
# tailbone_proxy_RESTRICTED_DOMAINS = ["google.com"]

# tailbone_turn_RESTIRCTED_DOMAINS = ["localhost"]
# tailbone_turn_SECRET = "notasecret"

# tailbone_mesh_TURN = False
# tailbone_mesh_WEBSOCKET = False
# tailbone_mesh_CHANNEL = True

## Seconds until room expires
# tailbone_mesh_ROOM_EXPIRATION = 86400


