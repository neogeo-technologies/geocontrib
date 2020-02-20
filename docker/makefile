# Geocontrib only
docker-geocontrib-up:
	docker-compose -f docker-compose.geocontrib.yaml up -d

docker-geocontrib-logs-f:
	docker-compose -f docker-compose.geocontrib.yaml logs -f

docker-geocontrib-ps:
	docker-compose -f docker-compose.geocontrib.yaml ps

docker-geocontrib-rm:
	docker-compose -f docker-compose.geocontrib.yaml stop
	docker-compose -f docker-compose.geocontrib.yaml rm -f

docker-geocontrib-clean-volumes:
	docker-compose -f docker-compose.geocontrib.yaml down --volumes --remove-orphans

docker-geocontrib-clean-images:
	docker-compose -f docker-compose.geocontrib.yaml down --rmi 'all' --remove-orphans

docker-geocontrib-clean-all:
	docker-compose -f docker-compose.geocontrib.yaml down --volumes --rmi 'all' --remove-orphans

# Geocontrib + geOrchestra minimal components
docker-all-up:
	docker-compose -f docker-compose.georchestra.yaml up -d

docker-all-rm:
	docker-compose -f docker-compose.georchestra.yaml stop
	docker-compose -f docker-compose.georchestra.yaml rm -f

docker-all-clean-volumes:
	docker-compose -f docker-compose.georchestra.yaml down --volumes --remove-orphans

docker-all-clean-images:
	docker-compose -f docker-compose.georchestra.yaml down --rmi 'all' --remove-orphans

docker-all-clean-all:
	docker-compose -f docker-compose.georchestra.yaml down --volumes --rmi 'all' --remove-orphans

docker-all-ps:
	docker-compose -f docker-compose.georchestra.yaml ps

docker-all-logs-f:
	docker-compose -f docker-compose.georchestra.yaml logs -f
