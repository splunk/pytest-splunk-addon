#!/bin/sh
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
echo args @@
sleep 10
exec pytest $@ tests
