describe('FlacJacket Homepage', () => {
  beforeEach(() => {
    cy.visit('/');
  });

  it('should load the homepage with dark mode', () => {
    // Check if the page has the dark theme class
    cy.get('html').should('have.class', 'dark');
    cy.get('header, nav').should('be.visible');
    cy.contains(/flacjacket|audio recognition/i).should('be.visible');
  });

  it('should toggle between dark and light mode', () => {
    // Get the initial theme class
    cy.get('html').then($html => {
      const hasDarkClass = $html.hasClass('dark');
      
      // Find and click the theme toggle button
      cy.get('button[aria-label="Toggle Dark Mode"]').click();
      
      // Wait for theme change
      cy.wait(500);
      
      // Check if theme changed
      if (hasDarkClass) {
        cy.get('html').should('not.have.class', 'dark');
      } else {
        cy.get('html').should('have.class', 'dark');
      }
    });
  });

  it('should have a URL input field and submit button', () => {
    cy.get('input[type="text"], input[type="url"], input:not([type])')
      .filter(':visible')
      .should('be.visible');
    
    cy.get('button')
      .contains(/submit|analyze|start/i)
      .should('be.visible');
  });

  it('should display recent analyses if any exist', () => {
    // Create a test analysis via API
    cy.createTestAnalysis('https://soundcloud.com/sparrowandbarbossa/maggies1').then(response => {
      // Refresh the page to see updated analyses list
      cy.visit('/');
      
      // Should see the analysis in the list
      cy.contains('sparrowandbarbossa/maggies1').should('be.visible');
    });
  });
});
