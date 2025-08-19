#!/bin/bash
echo args $@
cd /work
curl https://pyenv.run | bash
export PATH="~/.pyenv/bin:$PATH"
eval "$(pyenv init -)"
pyenv install 3.9.23
pyenv local 3.9.23
curl -sSL https://install.python-poetry.org | python - --version 2.1.4
export PATH="/root/.local/bin:$PATH"
source ~/.poetry/env
sleep 15
poetry install
exec poetry run pytest -vv $@
