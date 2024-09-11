import requests
import time

BASE_URL = 'http://localhost:5000'

def test_rate_limit(endpoint, method='GET', data=None, expected_limit=30):
    print(f"Testing rate limit for {method} {endpoint}")
    successful_requests = 0
    start_time = time.time()

    for i in range(expected_limit + 10):
        if method == 'GET':
            response = requests.get(f"{BASE_URL}{endpoint}")
        elif method == 'POST':
            response = requests.post(f"{BASE_URL}{endpoint}", json=data)
        elif method == 'PUT':
            response = requests.put(f"{BASE_URL}{endpoint}", json=data)
        elif method == 'DELETE':
            response = requests.delete(f"{BASE_URL}{endpoint}")
        
        if response.status_code == 200 or response.status_code == 201:
            successful_requests += 1
        elif response.status_code == 429:  # Too Many Requests
            print(f"Rate limit reached after {successful_requests} requests")
            break
        else:
            print(f"Unexpected status code: {response.status_code}")
        
        if i == expected_limit - 1:
            print(f"Expected rate limit ({expected_limit}) reached without 429 error")

    end_time = time.time()
    print(f"Time taken: {end_time - start_time:.2f} seconds")
    print(f"Successful requests: {successful_requests}")
    print("--------------------")

def run_tests():
    # Test GET /courses (30 per minute)
    test_rate_limit('/courses', 'GET')

    # Wait for a minute to reset the rate limit
    print("Waiting for 60 seconds to reset rate limit...")
    time.sleep(60)

    # Test POST /courses (10 per minute)
    course_data = {
        "title": "Test Course",
        "description": "This is a test course",
        "instructor": "Test Instructor",
        "duration": 10,
        "enrollment_limit": 20
    }
    test_rate_limit('/courses', 'POST', data=course_data, expected_limit=10)

    # Wait for a minute to reset the rate limit
    print("Waiting for 60 seconds to reset rate limit...")
    time.sleep(60)

    # Test GET /courses/1 (60 per minute)
    test_rate_limit('/courses/1', 'GET', expected_limit=60)

    # Note: We're not testing PUT and DELETE here to avoid modifying the database too much,
    # but you could add similar tests for those endpoints if needed.

if __name__ == '__main__':
    run_tests()