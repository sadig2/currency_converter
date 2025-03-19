cd fastapi-app
make genpriv
make genpub

docker-compose down -v
docker-compose build web --no-cache
docker-compose up -d