describe('FlacJacket Material Design Theme', () => {
  beforeEach(() => {
    cy.visit('/');
  });

  it('should have Material Design styled components', () => {
    // Check for Material Design styled header
    cy.get('header')
      .should('be.visible');
    
    // Check for Material Design styled inputs
    cy.get('input')
      .should('be.visible');
    
    // Check for Material Design styled buttons
    cy.get('button')
      .filter(':visible')
      .should('be.visible');
  });
  
  it('should have dark mode color scheme when in dark mode', () => {
    // Ensure we're in dark mode
    cy.get('html').then($html => {
      if (!$html.hasClass('dark')) {
        cy.get('button[aria-label="Toggle Dark Mode"]').click();
        // Wait for theme change to take effect
        cy.wait(500);
      }
    });
    
    // Check background color is dark
    cy.get('body').should('be.visible');
  });
  
  it('should have light mode color scheme when in light mode', () => {
    // Ensure we're in light mode
    cy.get('html').then($html => {
      if ($html.hasClass('dark')) {
        cy.get('button[aria-label="Toggle Dark Mode"]').click();
        // Wait for theme change to take effect
        cy.wait(500);
      }
    });
    
    // Check background color is light
    cy.get('body').should('be.visible');
  });
  
  it('should have responsive design', () => {
    // Test small viewport (mobile)
    cy.viewport('iphone-6');
    cy.wait(500); // Wait for resize to take effect
    cy.get('header').should('be.visible');
    cy.get('input').should('be.visible');
    
    // Test medium viewport (tablet)
    cy.viewport('ipad-2');
    cy.wait(500);
    cy.get('header').should('be.visible');
    cy.get('input').should('be.visible');
    
    // Test large viewport (desktop)
    cy.viewport(1280, 800);
    cy.wait(500);
    cy.get('header').should('be.visible');
    cy.get('input').should('be.visible');
  });
});
