# Geocontrib only
docker-geocontrib-build:
	docker-compose -f docker-compose.geocontrib-alone.yaml build

docker-geocontrib-up-d:
	docker-compose -f docker-compose.geocontrib-alone.yaml up -d

docker-geocontrib-logs-f:
	docker-compose -f docker-compose.geocontrib-alone.yaml logs -f

docker-geocontrib-ps:
	docker-compose -f docker-compose.geocontrib-alone.yaml ps

docker-geocontrib-down:
	docker-compose -f docker-compose.geocontrib-alone.yaml down

docker-geocontrib-down-clean-volumes:
	docker-compose -f docker-compose.geocontrib-alone.yaml down --volumes --remove-orphans

docker-geocontrib-down-clean-all:
	docker-compose -f docker-compose.geocontrib-alone.yaml down --volumes --rmi 'all' --remove-orphans

# Geocontrib + geOrchestra minimal components
docker-with-georchestra-build:
	docker-compose -f docker-compose.with-georchestra.yaml build

docker-with-georchestra-up-d:
	docker-compose -f docker-compose.with-georchestra.yaml up -d

docker-with-georchestra-logs-f:
	docker-compose -f docker-compose.with-georchestra.yaml logs -f

docker-with-georchestra-ps:
	docker-compose -f docker-compose.with-georchestra.yaml ps

docker-with-georchestra-down:
	docker-compose -f docker-compose.with-georchestra.yaml down

docker-with-georchestra-down-clean-volumes:
	docker-compose -f docker-compose.with-georchestra.yaml down --volumes --remove-orphans

docker-with-georchestra-down-clean-all:
	docker-compose -f docker-compose.with-georchestra.yaml down --volumes --rmi 'all' --remove-orphans
