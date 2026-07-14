import copy
import json
import os
import random
from locust import HttpUser, task, between, LoadTestShape, constant

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
    Locust load test for the Certificate Enroll API.
    Endpoint: POST /cert/v1/enroll
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
        """POST /cert/v1/enroll — request a new certificate enrollment."""
        payload = copy.deepcopy(self.base_payload)
        payload["symcOrderId"] = random.randint(3_000_000_000, 9_999_999_999)

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


class StepLoadShape:  # disabled — restore to (LoadTestShape) to re-enable
    """
    Automatically steps up user load to find the max RPS without failures.

    Steps:  10 → 25 → 50 → 100 → 200 users
    Each step runs for 3 minutes (180 s).

    Watch the Charts tab in the Locust UI:
      - RPS will rise with each step.
      - The moment Failures % > 0, the PREVIOUS step's RPS is your safe limit.
    """

    step_duration = 180   # seconds per step
    spawn_rate = 10       # users spawned per second when stepping up
    user_steps = [10, 25, 50, 100, 200]

    def tick(self):
        run_time = self.get_run_time()
        step_index = int(run_time // self.step_duration)
        if step_index >= len(self.user_steps):
            return None  # all steps done — stop the test
        return (self.user_steps[step_index], self.spawn_rate)


if __name__ == "__main__":
    """
    Run the step-load test (finds max RPS without failures automatically):
        locust -f load_tests/enroll_certificate.py --web-port 10842

    Run with explicit headless mode:
        locust -f load_tests/enroll_certificate.py --headless \
               --web-port 10842 --host http://localhost:8086
    """
    pass
