# API Documentation

## Overview

This document provides detailed information about the API endpoints available in the Advanced CI/CD Pipeline system.

## Base URL

```
https://api.advanced-cicd.example.com
```

## Authentication

All API endpoints require authentication using JWT tokens. Include the token in the Authorization header:

```
Authorization: Bearer <your_jwt_token>
```

## Endpoints

### Authentication

#### POST /api/auth/login
Authenticate user and get JWT token.

**Request Body:**
```json
{
  "username": "string",
  "password": "string"
}
```

**Response:**
```json
{
  "access_token": "string",
  "token_type": "bearer",
  "expires_in": 3600
}
```

### Metrics

#### GET /api/metrics
Get system metrics data.

**Response:**
```json
{
  "requestRate": [
    {
      "timestamp": "2024-03-20T10:00:00Z",
      "value": 100
    }
  ],
  "responseTime": [
    {
      "timestamp": "2024-03-20T10:00:00Z",
      "value": 50
    }
  ],
  "errorRate": [
    {
      "timestamp": "2024-03-20T10:00:00Z",
      "value": 2
    }
  ],
  "cpuUsage": [
    {
      "timestamp": "2024-03-20T10:00:00Z",
      "value": 30
    }
  ]
}
```

#### POST /api/metrics/record
Record new metrics data.

**Request Body:**
```json
{
  "method": "string",
  "route": "string",
  "status": "string",
  "duration": 0,
  "container": "string",
  "cpu_usage": 0
}
```

**Response:**
```json
{
  "status": "success"
}
```

### Alerts

#### GET /api/alerts
Get active alerts.

**Response:**
```json
[
  {
    "id": "string",
    "severity": "warning|critical",
    "title": "string",
    "description": "string",
    "timestamp": "2024-03-20T10:00:00Z"
  }
]
```

### Deployments

#### GET /api/deployments
Get deployment status for all environments.

**Response:**
```json
[
  {
    "environment": "string",
    "status": "success|in_progress|failed",
    "lastDeployed": "2024-03-20T10:00:00Z",
    "version": "string"
  }
]
```

#### POST /api/deployments
Trigger a new deployment.

**Request Body:**
```json
{
  "environment": "string",
  "version": "string",
  "strategy": "rolling|canary"
}
```

**Response:**
```json
{
  "deployment_id": "string",
  "status": "started",
  "timestamp": "2024-03-20T10:00:00Z"
}
```

### Builds

#### GET /api/builds
Get build history.

**Query Parameters:**
- `page` (integer): Page number
- `limit` (integer): Items per page
- `status` (string): Filter by status
- `environment` (string): Filter by environment

**Response:**
```json
{
  "builds": [
    {
      "id": "string",
      "status": "success|failed|in_progress",
      "environment": "string",
      "started_at": "2024-03-20T10:00:00Z",
      "completed_at": "2024-03-20T10:05:00Z",
      "version": "string",
      "commit": "string"
    }
  ],
  "total": 100,
  "page": 1,
  "limit": 10
}
```

#### POST /api/builds
Trigger a new build.

**Request Body:**
```json
{
  "branch": "string",
  "environment": "string"
}
```

**Response:**
```json
{
  "build_id": "string",
  "status": "started",
  "timestamp": "2024-03-20T10:00:00Z"
}
```

### Tests

#### GET /api/tests
Get test results.

**Query Parameters:**
- `type` (string): Test type (unit|integration|e2e)
- `environment` (string): Environment
- `build_id` (string): Build ID

**Response:**
```json
{
  "results": [
    {
      "id": "string",
      "name": "string",
      "status": "passed|failed|skipped",
      "duration": 0,
      "error": "string",
      "timestamp": "2024-03-20T10:00:00Z"
    }
  ],
  "summary": {
    "total": 100,
    "passed": 95,
    "failed": 5,
    "skipped": 0
  }
}
```

## Error Responses

All endpoints may return the following error responses:

### 400 Bad Request
```json
{
  "error": "string",
  "message": "string",
  "details": {}
}
```

### 401 Unauthorized
```json
{
  "error": "unauthorized",
  "message": "Invalid or missing authentication token"
}
```

### 403 Forbidden
```json
{
  "error": "forbidden",
  "message": "Insufficient permissions"
}
```

### 404 Not Found
```json
{
  "error": "not_found",
  "message": "Resource not found"
}
```

### 500 Internal Server Error
```json
{
  "error": "internal_server_error",
  "message": "An unexpected error occurred"
}
```

## Rate Limiting

API requests are limited to:
- 100 requests per minute per IP
- 1000 requests per hour per user

Rate limit headers are included in responses:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1616234400
```

## Webhooks

The API supports webhooks for real-time notifications. Register a webhook URL to receive notifications for:
- Build status changes
- Deployment events
- Alert triggers
- Test results

### POST /api/webhooks
Register a new webhook.

**Request Body:**
```json
{
  "url": "string",
  "events": ["build", "deployment", "alert", "test"],
  "secret": "string"
}
```

**Response:**
```json
{
  "id": "string",
  "url": "string",
  "events": ["build", "deployment", "alert", "test"],
  "active": true
}
```

## SDK Examples

### Python
```python
from advanced_cicd import Client

client = Client(
    base_url="https://api.advanced-cicd.example.com",
    token="your_jwt_token"
)

# Get metrics
metrics = client.get_metrics()

# Trigger deployment
deployment = client.create_deployment(
    environment="production",
    version="1.0.0",
    strategy="canary"
)
```

### JavaScript
```javascript
const { Client } = require('advanced-cicd');

const client = new Client({
  baseUrl: 'https://api.advanced-cicd.example.com',
  token: 'your_jwt_token'
});

// Get metrics
const metrics = await client.getMetrics();

// Trigger deployment
const deployment = await client.createDeployment({
  environment: 'production',
  version: '1.0.0',
  strategy: 'canary'
});
``` 