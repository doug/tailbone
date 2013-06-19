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


# this will extend the tailbone configuration file in tailbone/__init__.py

tailbone_JSONP = False
tailbone_METADATA = False

protected_PASSWORD = "secret"



# READ app yaml and import any defined Middleware objects
import yaml
middleware_list = []
with open("app.yaml") as f:
  appyaml = yaml.load(f)
  for include in appyaml.get("includes", []):
    try:
      module = __import__(include.replace("/", "."), 
                          globals(), locals(), ['Middleware'], -1)
      middleware = getattr(module, 'Middleware', None)
      if middleware:
        middleware_list.append(middleware)
    except ImportError:
      pass


def webapp_add_wsgi_middleware(app):
  """Loads any registered middleware, i.e. 
  included modules that have a Middleware class."""
  for middleware in middleware_list:
    app = middleware(app)
  return app