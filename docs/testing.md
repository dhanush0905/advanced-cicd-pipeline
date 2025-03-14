# Testing Guide

## Overview

This guide provides comprehensive information about testing practices, tools, and methodologies used in the Advanced CI/CD Pipeline project. It covers unit testing, integration testing, end-to-end testing, and performance testing.

## Testing Strategy

### Test Pyramid

```
┌─────────────────┐
│   E2E Tests     │ 10%
├─────────────────┤
│ Integration     │ 20%
│ Tests           │
├─────────────────┤
│   Unit Tests    │ 70%
└─────────────────┘
```

### Test Types

1. Unit Tests
   - Test individual components
   - Fast execution
   - High coverage
   - Mock external dependencies

2. Integration Tests
   - Test component interactions
   - Test API endpoints
   - Use test databases
   - Test external services

3. End-to-End Tests
   - Test complete workflows
   - Test user interactions
   - Test UI components
   - Test real environments

4. Performance Tests
   - Test system performance
   - Test load handling
   - Test stress conditions
   - Test scalability

## Unit Testing

### Python (pytest)

1. Test Structure:
```python
# tests/unit/test_service.py
import pytest
from app.services import process_data

class TestDataService:
    def setup_method(self):
        self.service = DataService()

    def test_process_data(self):
        input_data = [{"id": 1, "value": 10}]
        result = self.service.process_data(input_data)
        assert result["processed_value"] == 20

    def test_process_data_invalid(self):
        with pytest.raises(ValueError):
            self.service.process_data([])

    @pytest.mark.parametrize("input_data,expected", [
        ([{"id": 1, "value": 10}], 20),
        ([{"id": 2, "value": 20}], 40),
    ])
    def test_process_data_multiple(self, input_data, expected):
        result = self.service.process_data(input_data)
        assert result["processed_value"] == expected
```

2. Fixtures:
```python
# tests/conftest.py
import pytest
from app.database import Database

@pytest.fixture
def db():
    database = Database()
    database.connect()
    yield database
    database.disconnect()

@pytest.fixture
def test_data():
    return [
        {"id": 1, "value": 10},
        {"id": 2, "value": 20}
    ]
```

3. Mocking:
```python
from unittest.mock import Mock, patch

def test_external_service():
    with patch('app.services.external_api') as mock_api:
        mock_api.get_data.return_value = {"data": "test"}
        result = process_external_data()
        assert result == "test"
```

### TypeScript (Jest)

1. Component Testing:
```typescript
// tests/unit/DataComponent.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { DataComponent } from '../../src/components/DataComponent';

describe('DataComponent', () => {
  it('renders data correctly', () => {
    render(<DataComponent data={[{ id: 1, value: 10 }]} />);
    expect(screen.getByText('10')).toBeInTheDocument();
  });

  it('handles user interaction', () => {
    render(<DataComponent />);
    fireEvent.click(screen.getByText('Process'));
    expect(screen.getByText('Processing...')).toBeInTheDocument();
  });
});
```

2. Service Testing:
```typescript
// tests/unit/dataService.test.ts
import { DataService } from '../../src/services/dataService';

describe('DataService', () => {
  let service: DataService;

  beforeEach(() => {
    service = new DataService();
  });

  it('processes data correctly', () => {
    const result = service.processData([{ id: 1, value: 10 }]);
    expect(result.processedValue).toBe(20);
  });
});
```

## Integration Testing

### API Testing

1. FastAPI Tests:
```python
# tests/integration/test_api.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_get_data():
    response = client.get("/api/data")
    assert response.status_code == 200
    assert "data" in response.json()

def test_create_data():
    response = client.post(
        "/api/data",
        json={"id": 1, "value": 10}
    )
    assert response.status_code == 201
    assert response.json()["id"] == 1
```

2. Database Integration:
```python
# tests/integration/test_database.py
import pytest
from app.database import Database

@pytest.mark.asyncio
async def test_database_operations():
    db = Database()
    await db.connect()
    
    # Test insert
    result = await db.insert({"id": 1, "value": 10})
    assert result.id == 1
    
    # Test query
    data = await db.query({"id": 1})
    assert data.value == 10
    
    await db.disconnect()
```

### Service Integration

1. Microservice Testing:
```python
# tests/integration/test_services.py
from app.services import DataService, ProcessingService

def test_service_integration():
    data_service = DataService()
    processing_service = ProcessingService()
    
    # Test data flow
    data = data_service.get_data()
    result = processing_service.process(data)
    
    assert result.status == "processed"
    assert result.data.value == 20
```

## End-to-End Testing

### Cypress Tests

1. Basic Test:
```typescript
// tests/e2e/basic.cy.ts
describe('Basic Flow', () => {
  beforeEach(() => {
    cy.visit('/')
  });

  it('loads the dashboard', () => {
    cy.get('[data-testid="dashboard"]').should('exist');
    cy.get('[data-testid="metrics"]').should('be.visible');
  });

  it('processes data', () => {
    cy.get('[data-testid="input"]').type('test data');
    cy.get('[data-testid="submit"]').click();
    cy.get('[data-testid="result"]').should('contain', 'Processed');
  });
});
```

2. API Interaction:
```typescript
// tests/e2e/api.cy.ts
describe('API Integration', () => {
  it('fetches and displays data', () => {
    cy.intercept('GET', '/api/data').as('getData');
    cy.visit('/dashboard');
    
    cy.wait('@getData').then((interception) => {
      expect(interception.response.statusCode).to.equal(200);
    });
    
    cy.get('[data-testid="data-list"]').should('have.length.gt', 0);
  });
});
```

## Performance Testing

### k6 Load Testing

1. Basic Load Test:
```javascript
// tests/performance/load-test.js
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '30s', target: 20 },
    { duration: '1m', target: 20 },
    { duration: '30s', target: 0 },
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'],
    http_req_failed: ['rate<0.1'],
  },
};

export default function () {
  const response = http.get('http://test.k6.io');
  check(response, {
    'status is 200': (r) => r.status === 200,
    'response time < 500ms': (r) => r.timings.duration < 500,
  });
  sleep(1);
}
```

2. Stress Test:
```javascript
// tests/performance/stress-test.js
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '2m', target: 100 },
    { duration: '5m', target: 100 },
    { duration: '2m', target: 200 },
    { duration: '5m', target: 200 },
    { duration: '2m', target: 300 },
    { duration: '5m', target: 300 },
    { duration: '2m', target: 400 },
    { duration: '5m', target: 400 },
    { duration: '10m', target: 0 },
  ],
  thresholds: {
    http_req_duration: ['p(95)<1000'],
    http_req_failed: ['rate<0.2'],
  },
};

export default function () {
  const response = http.get('http://test.k6.io');
  check(response, {
    'status is 200': (r) => r.status === 200,
  });
  sleep(1);
}
```

## Test Coverage

### Python Coverage

1. Coverage Configuration:
```ini
# .coveragerc
[run]
source = src
omit = 
    */tests/*
    */migrations/*
    */__init__.py

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise NotImplementedError
    if __name__ == .__main__.:
    pass
```

2. Coverage Report:
```bash
pytest --cov=src --cov-report=html
```

### TypeScript Coverage

1. Jest Configuration:
```javascript
// jest.config.js
module.exports = {
  collectCoverageFrom: [
    'src/**/*.{ts,tsx}',
    '!src/**/*.d.ts',
    '!src/index.tsx',
  ],
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80,
    },
  },
};
```

2. Coverage Report:
```bash
npm run test:coverage
```

## Test Automation

### GitHub Actions

1. Test Workflow:
```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    
    - name: Set up Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18.x'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        npm ci
    
    - name: Run tests
      run: |
        pytest
        npm run test
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
```

### Jenkins Pipeline

1. Test Stage:
```groovy
// Jenkinsfile
pipeline {
    agent any
    
    stages {
        stage('Test') {
            steps {
                sh '''
                    python -m venv venv
                    source venv/bin/activate
                    pip install -r requirements.txt
                    pytest --cov=src --cov-report=xml
                    
                    npm ci
                    npm run test
                '''
            }
        }
    }
}
```

## Best Practices

### Test Organization

1. Directory Structure:
```
tests/
├── unit/
│   ├── test_services.py
│   └── test_models.py
├── integration/
│   ├── test_api.py
│   └── test_database.py
├── e2e/
│   ├── basic.cy.ts
│   └── api.cy.ts
└── performance/
    ├── load-test.js
    └── stress-test.js
```

2. Naming Conventions:
- Test files: `test_*.py` or `*.test.ts`
- Test classes: `Test*`
- Test methods: `test_*`

### Test Data Management

1. Fixtures:
```python
# tests/fixtures/data.py
TEST_DATA = {
    "users": [
        {"id": 1, "name": "Test User"},
        {"id": 2, "name": "Another User"}
    ],
    "settings": {
        "theme": "dark",
        "language": "en"
    }
}
```

2. Factories:
```python
# tests/factories/user.py
from factory import Factory, Sequence
from app.models import User

class UserFactory(Factory):
    class Meta:
        model = User
    
    name = Sequence(lambda n: f'User {n}')
    email = Sequence(lambda n: f'user{n}@example.com')
```

### Test Isolation

1. Database:
```python
@pytest.fixture(autouse=True)
async def clean_db():
    db = Database()
    await db.connect()
    yield
    await db.clean()
    await db.disconnect()
```

2. Cache:
```python
@pytest.fixture(autouse=True)
def clear_cache():
    cache.clear()
    yield
    cache.clear()
```

## Resources

### Documentation
- [pytest Documentation](https://docs.pytest.org/)
- [Jest Documentation](https://jestjs.io/)
- [Cypress Documentation](https://docs.cypress.io/)
- [k6 Documentation](https://k6.io/docs/)
- [Testing Library Documentation](https://testing-library.com/)

### Tools
- [pytest](https://pytest.org/)
- [Jest](https://jestjs.io/)
- [Cypress](https://www.cypress.io/)
- [k6](https://k6.io/)
- [coverage.py](https://coverage.readthedocs.io/)

### Learning Resources
- [Python Testing with pytest](https://pragprog.com/titles/bopytest/python-testing-with-pytest/)
- [Testing JavaScript Applications](https://www.manning.com/books/testing-javascript-applications)
- [End-to-End Testing with Cypress](https://www.cypress.io/blog/2019/05/02/cypress-is-really-great/)
- [Performance Testing with k6](https://k6.io/blog/) 