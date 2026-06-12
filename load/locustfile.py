from locust import HttpUser, task, between
import uuid


class VectorFlowLoadTester(HttpUser):
    # Simulate real human wait times
    wait_time = between(1, 5)

    @task(1)
    def health_check(self):
        """Verify the 500ms hard gate requirement."""
        self.client.get("/health")

    @task(3)
    def generate_stream(self):
        """Test the main streaming pipeline."""
        self.client.post("/api/v1/ai/stream", json={
            "message": "Draw a simple sword",
            "session_id": str(uuid.uuid4()),
            "system": "### PROTOCOL ### ROLE: SVG_GENERATOR. Output ONLY raw SVG code."
        })
