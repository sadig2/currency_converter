.PHONY: cmigrate
cmigrate:
	alembic revision --autogenerate -m "$(message)"

migrate:
	alembic upgrade head

genpriv:
	openssl genpkey -algorithm RSA -out private.pem -pkeyopt rsa_keygen_bits:4096

genpub:
	openssl rsa -pubout -in private.pem -out public.pem