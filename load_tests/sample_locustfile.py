from __future__ import annotations

import csv
import os
from pathlib import Path

from locust import HttpUser, between, task


def load_usernames() -> list[str]:
    input_file = Path(__file__).resolve().parent.parent / "inputs" / "sample" / "users.csv"

    with input_file.open(newline="", encoding="utf-8") as csv_file:
        rows = csv.DictReader(csv_file)
        return [row["username"] for row in rows if row.get("username")]


class SampleUser(HttpUser):
    wait_time = between(1, 2)
    usernames = load_usernames()

    @task
    def health_check(self) -> None:
        username = self.usernames[0] if self.usernames else "guest"
        path = os.getenv("LOCUST_SAMPLE_PATH", "/health")
        self.client.get(path, params={"username": username}, name=path)
