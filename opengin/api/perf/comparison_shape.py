from locust import LoadTestShape

class ComparisonShape(LoadTestShape):
    """
    Steps: 10 users for 3 min, 25 for 3 min, 50 for 3 min, 100 for 3 min.
    Total: 12 minutes. One continuous run = one chart.
    """
    stages = [
        {"duration": 180,  "users": 10,  "spawn_rate": 2},
        {"duration": 360,  "users": 25,  "spawn_rate": 5},
        {"duration": 540,  "users": 50,  "spawn_rate": 5},
        {"duration": 720,  "users": 100, "spawn_rate": 10},
    ]

    def tick(self):
        run_time = self.get_run_time()
        for stage in self.stages:
            if run_time < stage["duration"]:
                return stage["users"], stage["spawn_rate"]
        return None
