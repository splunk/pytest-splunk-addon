#!/bin/bash

cd /work
echo args $@
sleep 15
source ~/.poetry/env
poetry config virtualenvs.create false
poetry update
exec poetry run pytest $@
