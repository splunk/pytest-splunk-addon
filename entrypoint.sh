#!/bin/bash
echo args $@
cd /work
curl https://pyenv.run | bash
export PATH="~/.pyenv/bin:$PATH"
eval "$(pyenv init -)"
pyenv install 3.7.8
pyenv local 3.7.8
curl -sSL -sSL https://install.python-poetry.org | python
source ~/.poetry/env
sleep 15
poetry install -E docker
exec poetry run pytest -vv $@
