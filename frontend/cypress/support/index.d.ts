/// <reference types="cypress" />

declare namespace Cypress {
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
