from locust import HttpUser, task, between


class AuthenticatedUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        response = self.client.post(
            "/api/authenticate/login/",
            data={"username": "sadig", "password": "qwerty"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        if response.status_code != 200:
            raise Exception(f"Login failed: {response.text}")

        self.jwt_token = response.json().get("access_token")

    @task
    def protected_endpoint(self):
        headers = {"Authorization": f"Bearer {self.jwt_token}"}
        self.client.get("/api/currencies_converted", headers=headers)
