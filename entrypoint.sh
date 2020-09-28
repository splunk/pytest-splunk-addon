#!/bin/bash
echo check for splunk web
wait-for $SPLUNK_HOST:8000 -t 0 -- echo splunkweb is up
echo check for splunk mgmt
wait-for $SPLUNK_HOST:8089 -t 0 -- echo splunkmgmt is up
echo check for splunk hec
wait-for $SPLUNK_HOST:8088 -t 0 -- echo splunkhec is up

sleep 5

echo check for splunk web
wait-for $SPLUNK_HOST:8000 -t 0 -- echo splunkweb is up
echo check for splunk mgmt
wait-for $SPLUNK_HOST:8089 -t 0 -- echo splunkmgmt is up
echo check for splunk hec
wait-for $SPLUNK_HOST:8088 -t 0 -- echo splunkhec is up


cd /work
echo args $@
sleep 10
curl https://pyenv.run | bash ;\
export PATH="~/.pyenv/bin:$PATH" ;\
eval "$(pyenv init -)" ;\
pyenv install 3.7.8 ;\
pyenv local 3.7.8 ;\
curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python 
source ~/.poetry/env

poetry install -E docker

exec poetry run pytest $@
