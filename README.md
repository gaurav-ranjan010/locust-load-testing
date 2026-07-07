# Locust Load Testing Repository

This repository is structured to keep **Locust load test scripts** and their **test input files** organized and easy to maintain.

## Repository structure

```text
locust-load-testing/
├── README.md
├── load_tests/
│   └── sample_locustfile.py
└── inputs/
    └── sample/
        └── users.csv
```

## Folder purpose

### `load_tests/`
Store all Locust load test files in this folder.

Examples:
- API load tests
- Login flow tests
- Search or checkout flow tests
- Smoke or performance scenarios

Each Locust file can be created independently and kept in one central place for easier execution and maintenance.

### `inputs/`
Store all input files required by your load tests in this folder.

Examples:
- CSV files with usernames or IDs
- JSON payload files
- Request body templates
- Test data for specific scenarios

You can also create subfolders inside `inputs/` for each test suite, endpoint, or use case.

## Included sample files

This repository includes:

- `load_tests/sample_locustfile.py` - a sample Locust test file
- `inputs/sample/users.csv` - sample input data consumed by the sample test

The sample test shows how a Locust script can read test data from the `inputs/` directory.

## Prerequisites

Before running Locust, make sure you have:

- Python 3.9 or later installed
- `pip` available
- Access to the target application/API you want to test

## Install Locust

Install Locust with:

```bash
python -m pip install locust
```

To verify the installation:

```bash
locust --version
```

## How to add new load tests

1. Create a new Locust file inside `load_tests/`
2. Add any required input files inside `inputs/`
3. Keep related files grouped clearly, for example:

```text
load_tests/
├── login_locustfile.py
├── orders_locustfile.py
└── search_locustfile.py

inputs/
├── login/
│   └── users.csv
├── orders/
│   └── order_payloads.json
└── search/
    └── keywords.csv
```

## Sample Locust file behavior

The sample file:

- uses `HttpUser`
- sends a GET request
- reads user names from `inputs/sample/users.csv`
- demonstrates how to keep test data separate from test logic

By default, it sends a request to:

```text
/health
```

The sample request path can be changed using an environment variable:

```bash
export LOCUST_SAMPLE_PATH=/api/health
```

## How to run the load test

From the repository root, run:

```bash
locust -f load_tests/sample_locustfile.py
```

After running the command, Locust starts a web UI locally by default.

Open the UI in your browser:

```text
http://localhost:8089
```

## How to run with a target host

If your test script does not define a host internally, provide it at runtime:

```bash
locust -f load_tests/sample_locustfile.py --host http://localhost:8000
```

Replace `http://localhost:8000` with the base URL of the application you want to test.

## How to start the test from Locust UI

Once the Locust UI opens:

1. Enter the **Number of users**
2. Enter the **Ramp up / Spawn rate**
3. Confirm or provide the **Host** value
4. Click **Start swarming**

Locust will begin generating traffic against the configured target.

## How to check load test results in the Locust UI

The Locust UI provides multiple sections to review the test results.

### 1. Statistics

This is the main screen used to check performance results.

Important columns commonly shown here include:

- **Type** - request type such as GET or POST
- **Name** - request name or endpoint
- **Request Count** - total number of requests sent
- **Failure Count** - total failed requests
- **Median** - median response time
- **95%ile / 99%ile** - high percentile response times
- **Average** - average response time
- **Min / Max** - minimum and maximum response times
- **Average size** - average response payload size
- **Current RPS** - current requests per second
- **Current Failures/s** - failure rate per second

Use this screen to understand:

- response time behavior
- throughput
- endpoint-level failures
- latency trends

### 2. Charts

The charts section helps visualize:

- number of users over time
- requests per second
- response times
- failures over time

Use charts when you want to observe:

- ramp-up impact
- stability during sustained load
- spikes in latency
- whether failures start at a particular concurrency level

### 3. Failures

The failures section shows:

- failed endpoints
- error messages
- grouped exception information

Use this view to identify:

- API errors
- connection issues
- timeout problems
- unexpected response behavior

### 4. Exceptions

If your Locust scripts raise Python exceptions, they will appear here.

This helps debug:

- broken test scripts
- bad input data
- parsing issues
- code errors inside your Locust tasks

### 5. Download data

Locust also allows exporting results such as CSV reports depending on how you run it.

These exports are useful for:

- sharing results
- comparing multiple test runs
- storing performance history
- building custom reports

## How to interpret the results

When reviewing Locust results, focus on:

### Response time
- Are average and percentile response times acceptable?
- Are p95 and p99 much higher than average?

### Failure rate
- Are requests failing under load?
- Do failures start only after a certain user count?

### Throughput
- Is the system handling the desired requests per second?
- Does throughput flatten while users increase?

### Stability
- Does performance remain steady during the test?
- Do charts show spikes, degradation, or increasing errors?

## Recommended workflow for new tests

1. Add or update input data in `inputs/`
2. Create or update the Locust script in `load_tests/`
3. Run Locust locally
4. Open the Locust UI
5. Start with a small number of users
6. Increase load gradually
7. Review statistics, charts, and failures
8. Adjust the script or data as needed

## Notes

- Keep test scripts inside `load_tests/` only
- Keep all input datasets inside `inputs/`
- Use separate input subfolders for clarity when the project grows
- Keep environment-specific host values outside the code when possible and pass them at runtime
- Start with smaller loads before running high concurrency tests

## Next suggested additions

As the repository grows, you can add:

- more Locust files under `load_tests/`
- more CSV/JSON input datasets under `inputs/`
- environment-specific run commands
- CSV result export commands
- CI workflows for automated performance test execution