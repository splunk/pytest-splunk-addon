init:
	pip install -r requirements.txt

test:
	pytest tests

docker-volume:
	docker-compose stop
	docker-compose rm splunk
	docker volume rm pytest-splunk-addon-etc || true
	docker volume create pytest-splunk-addon-etc
	docker container create --name dummy -v pytest-splunk-addon-etc:/work/splunk-etc registry.access.redhat.com/ubi8/ubi
	docker cp tests/addons/ dummy:/work/splunk-etc/apps/
	docker rm dummy
