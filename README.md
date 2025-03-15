# Project Setup:

## Overview

In this project, we interact with a third-party bank-side API to fetch financial data. Since users' behavior can be unpredictable and we don't want to overload the bank's API with too frequent requests, we have set up scheduler to sync the required data into our local cache (Redis) spinning on docker container. This allows us to serve the data from our cache without repeatedly querying the external API, improving the performance and reducing load on the external service.

  
### Solution
To mitigate this, we implemented a scheduler that automatically syncs the required data into a Redis cache at set intervals, and the data is then fetched from Redis when users request it via our API. This reduces the number of external requests and ensures that our API remains responsive, even during high traffic.

### Security:

Our app uses jwt token for authentication and auhtorization - hence one can not perform any request successfully without token. As well as one user can not see data of the other user.

## Project Architecture

4 containers: redis, celery, postgres and web api

- **API**: The main API is built using FastAPI, and it fetches data from Redis as well as postgees (more static data) rather than directly from the bank-side APi. For database interaction it uses async sqlalchemy, for data validation - Pydantic.
- **Celery**: We use Celery for scheduling background tasks that handle syncing data between Redis and the bank-side API.


    


# Deploy:

chmod +x deploy.sh

./deploy.sh  - simply make this file executable





# Workflow 



/docs - for swagger

/api/authenticate/login - to login to the app , to authenticate the user

/api/wallets/{wallet_name}/currencies_converted - will fetch currencies of specific  wallet of user and convert them all to pln and return the sum with list of new currencies

/api/currencies_convertes - will fetch all converted currencies of current active user and convert them all to pln and return the sum with list of new currencies

/api/wallet - will create new wallet (user can have 1 wallet with same name)

/api/wallet/{wallet_id} - will update wallet data



