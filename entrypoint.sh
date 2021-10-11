#
# Copyright 2021 Splunk Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#!/bin/bash
echo args $@
cd /work
curl https://pyenv.run | bash ;\
export PATH="~/.pyenv/bin:$PATH" ;\
eval "$(pyenv init -)" ;\
pyenv install 3.7.8 ;\
pyenv local 3.7.8 ;\
curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python 
source ~/.poetry/env
sleep 15
poetry install -E docker
exec poetry run pytest -vv $@
