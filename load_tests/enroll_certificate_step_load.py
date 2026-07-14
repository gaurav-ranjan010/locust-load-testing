import copy
import json
import os
import random
from locust import HttpUser, task, constant, LoadTestShape

SSL_CLIENT_CERT = (
    "MIIEEjCCAvqgAwIBAgIJAIoTVi+Ak0wJMA0GCSqGSIb3DQEBBQUAMGMxCzAJBgNV"
    "BAYTAlVTMQ0wCwYDVQQIEwRVdGFoMQ0wCwYDVQQHEwRPcmVtMRAwDgYDVQQKEwdP"
    "cmdOYW1lMSQwIgYDVQQDExtzYW1sLmxvY2FsaG9zdC5kaWdpY2VydC5jb20wHhcN"
    "MTcwNTE5MTQ0NjMzWhcNMjcwNTE3MTQ0NjMzWjBjMQswCQYDVQQGEwJVUzENMAsG"
    "A1UECBMEVXRhaDENMAsGA1UEBxMET3JlbTEQMA4GA1UEChMHT3JnTmFtZTEkMCIG"
    "A1UEAxMbc2FtbC5sb2NhbGhvc3QuZGlnaWNlcnQuY29tMIIBIjANBgkqhkiG9w0B"
    "AQEFAAOCAQ8AMIIBCgKCAQEA8RszzJlfjTm8OUQBlFvMJOFUCtkyL2WY/oFsn32s"
    "o76NR9bkN4NSd5Uvw2q2qAPv/qW9+2yJw2AE4dwVh6IddvKaZgfXdrpaP7SakupY"
    "o4wjdF5faGCISyf1X7WuEZ/8sQGpCNLRMHebpNTuimSmD2wD/hlh0vKChuOIo+dX"
    "XthgjrxTX5mrrz+ReCnUK0dwFp/moJLVK5SUZzd7z9JyPtvnZVyx0gvSZwzoTXKk"
    "b5Nr60Mc1e37uErzSovDxAJf08A+V+6d6coTcd5xFCp1r/bWCPyn0xKR9HYvrMyW"
    "wpCTkF4RJzMeR6EkjDbk1pqve9291/zu6zhpLctwWOFCjQIDAQABo4HIMIHFMB0G"
    "A1UdDgQWBBQk18O+hbjTa9W2mpwmphzLnwKQITCBlQYDVR0jBIGNMIGKgBQk18O+"
    "hbjTa9W2mpwmphzLnwKQIaFnpGUwYzELMAkGA1UEBhMCVVMxDTALBgNVBAgTBFV0"
    "YWgxDTALBgNVBAcTBE9yZW0xEDAOBgNVBAoTB09yZ05hbWUxJDAiBgNVBAMTG3Nh"
    "bWwubG9jYWxob3N0LmRpZ2ljZXJ0LmNvbYIJAIoTVi+Ak0wJMAwGA1UdEwQFMAMB"
    "Af8wDQYJKoZIhvcNAQEFBQADggEBAIbiNxa+faNEKJlvCWLVp4RpYzrMY3877hNC"
    "PAL5aqRSKwYAupOCDDDnFgb+QNrWTAFQIcxgYpyHpB8Oeu8ZjOA+7xVtVdd2q2CX"
    "zI0yE0uHMIDP+/2GyY0IBQ0VxepgFGoL9OPSQwrvlQZo36KHjRD81/FkBwvpotuF"
    "qMkgmWqm3606BNCEsDuIXlvSe15ipC7J/RVctdQEBC1+4kxSUstUlwxCGVfNYzPd"
    "Lk/E8LgAoLQEnomJkrtBPXzTyzYb9q5rlzwGkfhTU6EH4VUBoF0mTxx0ICQgqsXI"
    "EMqOUBzwwxEJPKcDEfGHkJmoJ6XXaOimQN9IQf3x/UqfgHn42ZI="
)


class EnrollCertificateUser(HttpUser):
    """
    Load test user for POST /cert/v1/enroll.
    Payload loaded from inputs/sample/enroll_certificate.json.
    symcOrderId is randomised per request to avoid duplicates.
    """

    wait_time = constant(0)
    host = "http://localhost:8086"

    def on_start(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        json_file_path = os.path.join(
            current_dir, "..", "inputs", "sample", "enroll_certificate.json"
        )
        with open(json_file_path, "r") as f:
            self.base_payload = json.load(f)

        self.headers = {
            "Content-Type": "application/json",
            "X-SSL-Client-Certificate": SSL_CLIENT_CERT,
        }

    @task
    def enroll_certificate(self):
        """POST /cert/v1/enroll"""
        payload = copy.deepcopy(self.base_payload)
        payload["symcOrderId"] = random.randint(1_000_000_000, 9_999_999_999)

        with self.client.post(
            "/cert/v1/enroll",
            json=payload,
            headers=self.headers,
            catch_response=True,
            name="Enroll Certificate",
        ) as response:
            if response.status_code in (200, 201):
                response.success()
            else:
                response.failure(
                    f"Unexpected status {response.status_code}: {response.text[:200]}"
                )


class HourlyStepLoadShape(LoadTestShape):
    """
    1-hour step-load test for POST /cert/v1/enroll.

    Each step runs for 10 minutes:

        0 – 10 min  →   5 users
       10 – 20 min  →  10 users
       20 – 30 min  →  15 users
       30 – 40 min  →  20 users
       40 – 50 min  →  25 users
       50 – 60 min  →  30 users

    How to read the Charts tab:
      - RPS will rise with each step.
      - Watch the Failures line — the step where it first lifts off zero
        marks the saturation point. The previous step's RPS is the
        maximum safe throughput the API can sustain without failures.
    """

    # (duration_seconds, users) pairs — cumulative time boundaries
    steps = [
        (10 * 60,   5),   # 0  – 10 min →  5 users
        (20 * 60,  10),   # 10 – 20 min → 10 users
        (30 * 60,  15),   # 20 – 30 min → 15 users
        (40 * 60,  20),   # 30 – 40 min → 20 users
        (50 * 60,  25),   # 40 – 50 min → 25 users
        (60 * 60,  30),   # 50 – 60 min → 30 users
    ]
    spawn_rate = 5  # users spawned per second at each step transition

    def tick(self):
        run_time = self.get_run_time()
        for boundary, user_count in self.steps:
            if run_time < boundary:
                return (user_count, self.spawn_rate)
        return None  # all 6 steps done — stop the test


if __name__ == "__main__":
    """
    Start with web UI (recommended — watch Charts tab live):
        locust -f load_tests/enroll_certificate_step_load.py \\
               --host http://localhost:8086 --web-port 10842

    Then click Start in the browser. Users/ramp-up are controlled by
    HourlyStepLoadShape and cannot be changed from the UI.

    Headless with HTML report:
        locust -f load_tests/enroll_certificate_step_load.py \\
               --host http://localhost:8086 --headless \\
               --html reports/enroll_1hr_step_report.html
    """
    pass
