make genpriv
make genpub

docker-compose build web --no-cache
docker-compose up -d