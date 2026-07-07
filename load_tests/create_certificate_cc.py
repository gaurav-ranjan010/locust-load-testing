import json
import os
import random
import string
from locust import HttpUser, task, between


class CertificateOrderUser(HttpUser):
    """
    Locust load test for DigiCert SSL Certificate Order API
    """
    # Wait time between tasks (in seconds)
    wait_time = between(1, 3)
    
    # Base URL for the API
    host = "https://localhost.digicert.dev"
    
    def on_start(self):
        """
        Load the request payload from JSON file when the user starts
        """
        # Get the path to the JSON input file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        json_file_path = os.path.join(
            current_dir, 
            "..", 
            "inputs", 
            "sample", 
            "create_certificate_cc.json"
        )
        
        # Load the JSON payload
        with open(json_file_path, 'r') as f:
            self.payload = json.load(f)
        
        # Set the headers
        self.headers = {
            "X-DC-DEVKEY": "BJ7GTD7W6URYK2V2X3YFTR4HO4FUDJSF3EXCVOPDSDADAHNTQQMCFC6LKW2S3QRGZIMJ7ET4QOHXXIKKQ",
            "Content-Type": "application/json",
            "Cookie": "PHPSESSID=JbpSbC3TrnoSDiNysqyYiQ3C7cO5s6zVxN6bFRkZb0bDRG60"
        }
    
    def generate_random_domain(self):
        """
        Generate a random domain name for common_name
        """
        # Generate random subdomain (5-10 characters)
        subdomain_length = random.randint(5, 10)
        subdomain = ''.join(random.choices(string.ascii_lowercase, k=subdomain_length))
        
        # Random TLD
        tlds = ['com', 'org', 'net', 'io', 'dev', 'app', 'tech', 'info']
        tld = random.choice(tlds)
        
        return f"{subdomain}.{tld}"
    
    @task
    def create_certificate_order(self):
        """
        POST request to create SSL certificate order
        """
        # Create a copy of the payload and set random common_name
        request_payload = self.payload.copy()
        request_payload['certificate']['common_name'] = self.generate_random_domain()
        
        with self.client.post(
            "/services/v2/order/certificate/ssl_dv_rapidssl",
            json=request_payload,
            headers=self.headers,
            catch_response=True,
            name="Create SSL Certificate Order"
        ) as response:
            if response.status_code == 200 or response.status_code == 201:
                response.success()
            else:
                response.failure(f"Failed with status code: {response.status_code}")


if __name__ == "__main__":
    """
    Run the load test from command line:
    locust -f load_tests/create_certificate_cc.py --web-port 10842
    
    Or with specific parameters:
    locust -f load_tests/create_certificate_cc.py --users 10 --spawn-rate 2 --web-port 10842 --host https://localhost.digicert.dev
    """
    pass
