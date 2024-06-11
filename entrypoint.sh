#!/bin/bash
echo args $@
cd /work
curl https://pyenv.run | bash
export PATH="~/.pyenv/bin:$PATH"
eval "$(pyenv init -)"
pyenv install 3.7.8
pyenv local 3.7.8
curl -sSL https://install.python-poetry.org | python - --version 1.5.1
export PATH="/root/.local/bin:$PATH"
source ~/.poetry/env
sleep 15
poetry install
exec poetry run pytest -vv --junitxml=/work/test-results/test.xml $@
