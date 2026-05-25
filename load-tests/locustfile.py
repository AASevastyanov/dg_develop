from locust import HttpUser, between, task


class PublicApiUser(HttpUser):
    """
    Base scenario for stress-testing public API endpoints.
    """

    wait_time = between(1, 2)

    @task(3)
    def events_list(self):
        self.client.get("/api/v1/events/", name="GET /api/v1/events/")

    @task(1)
    def health_endpoint(self):
        self.client.get("/api/v1/", name="GET /api/v1/")
