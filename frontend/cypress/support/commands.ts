// ***********************************************
// This example commands.ts shows you how to
// create various custom commands and overwrite
// existing commands.
//
// For more comprehensive examples of custom
// commands please read more here:
// https://on.cypress.io/custom-commands
// ***********************************************

declare global {
  namespace Cypress {
    interface Chainable {
      /**
       * Custom command to submit a URL for analysis
       * @example cy.submitAnalysis('https://soundcloud.com/example/test-track')
       */
      submitAnalysis(url: string): Chainable<void>
      
      /**
       * Custom command to toggle the theme
       * @example cy.toggleTheme()
       */
      toggleTheme(): Chainable<void>
      
      /**
       * Custom command to create a test analysis directly via API
       * @example cy.createTestAnalysis('https://soundcloud.com/example/test-track')
       */
      createTestAnalysis(url: string): Chainable<any>

      /**
       * Custom command to get all analyses via API
       * @example cy.getAnalyses()
       */
      getAnalyses(): Chainable<any>
    }
  }
}

// Submit analysis form
Cypress.Commands.add('submitAnalysis', (url: string) => {
  cy.get('input[type="text"], input[type="url"], input:not([type])')
    .filter(':visible')
    .first()
    .type(url);
  
  cy.get('button')
    .contains(/submit|analyze|start/i)
    .click();
});

// Toggle theme
Cypress.Commands.add('toggleTheme', () => {
  cy.get('button[aria-label="Toggle Dark Mode"]').click();
});

// Create analysis via API
Cypress.Commands.add('createTestAnalysis', (url: string) => {
  return cy.request({
    method: 'POST',
    url: `${Cypress.env('apiUrl')}/analysis`,
    body: { url },
    headers: { 'Content-Type': 'application/json' }
  });
});

// Get all analyses via API
Cypress.Commands.add('getAnalyses', () => {
  return cy.request(`${Cypress.env('apiUrl')}/analyses`);
});

export {};
