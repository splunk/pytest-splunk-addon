#!/bin/bash
echo args $@
cd /work
curl -sSL https://install.python-poetry.org | python3.9 - --version 2.1.4
export PATH="/root/.local/bin:$PATH"
sleep 15
poetry install
exec poetry run pytest -vv $@
