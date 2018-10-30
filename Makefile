export APP=keyword_api
export DC_PREFIX= $(shell pwd)/docker-compose

#other variable definition
DC    := 'docker-compose'

api:
	${DC} -f ${DC_PREFIX}-api.yml up --build -d

api-log:
	${DC} -f ${DC_PREFIX}-api.yml logs --build -d

api-stop:
	${DC} -f ${DC_PREFIX}-api.yml down

network-stop:
	docker network rm ${APP}

network:
	@docker network create ${APP} 2> /dev/null; true

up: network api

down: api-stop network-stop
