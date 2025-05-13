up:
	docker compose -f docker-compose-local.yaml up -d

down:
	docker compose -f docker-compose-local.yaml down -v

stop:
	docker stop $(docker ps -q)

restart:
	docker compose -f docker-compose-local.yaml restart

delete:
	docker rm $(docker ps -a -q)

delete-images:
	docker rmi $(docker images -q)

create-db:
	alembic revision --autogenerate -m "Create DB"
	alembic upgrade head


