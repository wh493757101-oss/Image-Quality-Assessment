import time
from locust import HttpUser, task, between

try:
    with open("out.png", "rb") as f:
        IMAGE_DATA = f.read()
except FileNotFoundError:
    print("  Warning: out.png not found, using dummy data (route testing only, may fail)")
    IMAGE_DATA = b"fake_image_data"

class IQALoadTester(HttpUser):
    wait_time = between(1, 3)

    @task
    def test_async_evaluation_flow(self):
        files = {"pred_file": ("out.png", IMAGE_DATA, "image/png")}
        with self.client.post("/api/v1/submit_eval", files=files, name="1_Submit_Task", catch_response=True) as response:
            if response.status_code == 202:
                response.success()
                task_id = response.json().get("task_id")
            else:
                response.failure(f"Request rejected: {response.status_code}")
                return
        while True:
            time.sleep(1)

            with self.client.get(f"/api/v1/task_status/{task_id}", name="2_Poll_Status", catch_response=True) as poll_res:
                if poll_res.status_code == 200:
                    status_data = poll_res.json()
                    status = status_data.get("status", "")

                    if status.startswith("completed"):
                        poll_res.success()
                        break
                    elif status == "failed":
                        poll_res.failure("Backend processing failed")
                        break
                else:
                    poll_res.failure(f"Query failed: {poll_res.status_code}")
                    break