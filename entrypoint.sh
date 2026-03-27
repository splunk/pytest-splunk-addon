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
if [ -n "$GH_TOKEN" ]; then
  git config --global --add url."https://$GH_TOKEN@github.com".insteadOf https://github.com
  git config --global --add url."https://$GH_TOKEN@github.com".insteadOf ssh://git@github.com
fi
sleep 15
poetry install
exec poetry run pytest -vv $@
