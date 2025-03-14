declare namespace Cypress {
  interface Chainable {
    login(username: string, password: string): Chainable<void>;
    logout(): Chainable<void>;
    resetDatabase(): Chainable<void>;
    seedTestData(): Chainable<void>;
  }
}

// Login command
Cypress.Commands.add('login', (username: string, password: string) => {
  cy.request({
    method: 'POST',
    url: `${Cypress.env('apiUrl')}/api/auth/login`,
    body: {
      username,
      password,
    },
  }).then((response) => {
    window.localStorage.setItem('token', response.body.token);
  });
});

// Logout command
Cypress.Commands.add('logout', () => {
  cy.request({
    method: 'POST',
    url: `${Cypress.env('apiUrl')}/api/auth/logout`,
    headers: {
      Authorization: `Bearer ${window.localStorage.getItem('token')}`,
    },
  }).then(() => {
    window.localStorage.removeItem('token');
  });
});

// Reset database command (for test isolation)
Cypress.Commands.add('resetDatabase', () => {
  cy.request({
    method: 'POST',
    url: `${Cypress.env('apiUrl')}/api/testing/reset`,
    headers: {
      'x-testing-key': Cypress.env('testingKey'),
    },
  });
});

// Seed test data command
Cypress.Commands.add('seedTestData', () => {
  cy.request({
    method: 'POST',
    url: `${Cypress.env('apiUrl')}/api/testing/seed`,
    headers: {
      'x-testing-key': Cypress.env('testingKey'),
    },
  });
});

// Preserve cookies between tests
beforeEach(() => {
  Cypress.Cookies.preserveOnce('session_id', 'remember_token');
});

// Clear local storage between tests unless explicitly preserved
beforeEach(() => {
  const preserveLocalStorage = Cypress.env('preserveLocalStorage');
  if (!preserveLocalStorage) {
    cy.clearLocalStorage();
  }
});

// Add custom error handling
Cypress.on('uncaught:exception', (err) => {
  // Prevent Cypress from failing the test for uncaught exceptions
  console.error('Uncaught exception:', err);
  return false;
});

// Add custom logging
Cypress.on('log:added', (log) => {
  if (log.displayName === 'xhr' && log.state === 'failed') {
    console.error('XHR Failed:', log);
  }
});

// Add custom assertions
chai.Assertion.addMethod('containIgnoreCase', function(expectedText: string) {
  const text = this._obj.toLowerCase();
  const expected = expectedText.toLowerCase();
  this.assert(
    text.includes(expected),
    `expected #{this} to contain case-insensitive '${expectedText}'`,
    `expected #{this} not to contain case-insensitive '${expectedText}'`
  );
}); 