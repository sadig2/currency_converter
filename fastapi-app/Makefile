.PHONY: cmigrate
cmigrate:
	alembic revision --autogenerate -m "$(message)"

migrate:
	alembic upgrade head

genpriv:
	openssl genpkey -algorithm RSA -out private.pem -pkeyopt rsa_keygen_bits:4096

genpub:
	openssl rsa -pubout -in private.pem -out public.pem

force:
	docker compose up --build --force-recreate

get_redis_key:
	docker exec -it fastapi-app-redis redis-cli HGET trade USD

drop:
	docker-compose exec db psql -U clanzu -d clanzu_db -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
