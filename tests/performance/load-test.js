import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate } from 'k6/metrics';

// Custom metrics
const errorRate = new Rate('errors');

// Test configuration
export const options = {
  stages: [
    { duration: '1m', target: 50 },   // Ramp up to 50 users over 1 minute
    { duration: '3m', target: 50 },   // Stay at 50 users for 3 minutes
    { duration: '1m', target: 100 },  // Ramp up to 100 users over 1 minute
    { duration: '3m', target: 100 },  // Stay at 100 users for 3 minutes
    { duration: '1m', target: 0 },    // Ramp down to 0 users
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'], // 95% of requests must complete within 500ms
    http_req_failed: ['rate<0.01'],   // Less than 1% of requests can fail
    errors: ['rate<0.01'],            // Less than 1% custom error rate
  },
};

// Test setup
export function setup() {
  const loginRes = http.post(`${__ENV.URL}/api/auth/login`, {
    username: 'testuser',
    password: 'testpass',
  });
  
  return {
    token: loginRes.json('token'),
  };
}

// Default test function
export default function(data) {
  const params = {
    headers: {
      'Authorization': `Bearer ${data.token}`,
      'Content-Type': 'application/json',
    },
  };

  // Test scenarios
  group('API Health Check', () => {
    const healthRes = http.get(`${__ENV.URL}/api/health`);
    check(healthRes, {
      'health check status is 200': (r) => r.status === 200,
    });
  });

  group('User Profile', () => {
    const profileRes = http.get(`${__ENV.URL}/api/profile`, params);
    check(profileRes, {
      'profile status is 200': (r) => r.status === 200,
      'profile has correct data': (r) => r.json('username') === 'testuser',
    });
  });

  group('Data Operations', () => {
    // Create data
    const createRes = http.post(`${__ENV.URL}/api/data`, {
      title: 'Test Item',
      description: 'Test Description',
    }, params);
    
    check(createRes, {
      'create status is 201': (r) => r.status === 201,
      'created item has id': (r) => r.json('id') !== undefined,
    });

    // Read data
    const itemId = createRes.json('id');
    const readRes = http.get(`${__ENV.URL}/api/data/${itemId}`, params);
    
    check(readRes, {
      'read status is 200': (r) => r.status === 200,
      'read item has correct title': (r) => r.json('title') === 'Test Item',
    });

    // Update data
    const updateRes = http.put(`${__ENV.URL}/api/data/${itemId}`, {
      title: 'Updated Test Item',
    }, params);
    
    check(updateRes, {
      'update status is 200': (r) => r.status === 200,
      'item was updated': (r) => r.json('title') === 'Updated Test Item',
    });

    // Delete data
    const deleteRes = http.del(`${__ENV.URL}/api/data/${itemId}`, null, params);
    
    check(deleteRes, {
      'delete status is 204': (r) => r.status === 204,
    });
  });

  // Random sleep between requests to simulate real user behavior
  sleep(Math.random() * 3 + 1); // Random sleep between 1-4 seconds
}

// Test teardown
export function teardown(data) {
  // Cleanup any test data or logout
  http.post(`${__ENV.URL}/api/auth/logout`, null, {
    headers: {
      'Authorization': `Bearer ${data.token}`,
    },
  });
} 