#!/bin/bash

cd /work
echo args $@
sleep 15
source ~/.poetry/env
exec poetry run pytest $@
