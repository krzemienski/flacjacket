describe('FlacJacket Analysis Flow', () => {
  it('should submit a URL for analysis and show loading state', () => {
    cy.visit('/');
    
    const testUrl = 'https://soundcloud.com/sparrowandbarbossa/maggies1';
    
    // Submit a URL for analysis
    cy.submitAnalysis(testUrl);
    
    // Should show loading state or redirect to analysis page
    cy.contains(/loading|processing|analyzing/i, { timeout: 10000 }).should('be.visible');
  });
  
  it('should create an analysis via API and view its details', () => {
    // Create analysis via API first
    cy.createTestAnalysis('https://soundcloud.com/sparrowandbarbossa/maggies1').then(response => {
      const analysisId = response.body.id;
      
      // Visit the analysis details page
      cy.visit(`/analysis/${analysisId}`);
      
      // Should show the analysis details
      cy.contains('sparrowandbarbossa/maggies1').should('be.visible');
      
      // Check status indicator is visible
      cy.contains(/pending|processing|completed|failed/i).should('be.visible');
    });
  });
  
  it('should list all analyses', () => {
    // Create multiple test analyses
    cy.createTestAnalysis('https://soundcloud.com/soundnightclub/sparrow-barbossa-live-at-sound-on-031624');
    cy.createTestAnalysis('https://soundcloud.com/sweetmusicofc/sweet-mixtape-135-sparrow-barbossa');
    
    // Visit analyses list page or homepage
    cy.visit('/');
    
    // Should see the analyses in the list
    cy.contains('sparrow-barbossa-live-at-sound-on-031624').should('be.visible');
    cy.contains('sweet-mixtape-135-sparrow-barbossa').should('be.visible');
  });
  
  it('should show appropriate UI feedback for different analysis states', () => {
    // Get analyses from the API to find examples of different states
    cy.getAnalyses().then(response => {
      const analyses = response.body.analyses;
      
      if (analyses.length > 0) {
        // Find analyses with different statuses if possible
        const pendingAnalysis = analyses.find(a => a.status === 'pending');
        const failedAnalysis = analyses.find(a => a.status === 'failed');
        const completedAnalysis = analyses.find(a => a.status === 'completed');
        
        // Check UI for a failed analysis
        if (failedAnalysis) {
          cy.visit(`/analysis/${failedAnalysis.id}`);
          cy.contains(/failed|error|could not/i).should('be.visible');
          cy.contains(failedAnalysis.error_message || 'Error').should('be.visible');
        }
        
        // Check UI for a completed analysis (if one exists)
        if (completedAnalysis) {
          cy.visit(`/analysis/${completedAnalysis.id}`);
          cy.contains(/completed|success|tracks found/i).should('be.visible');
          if (completedAnalysis.tracks && completedAnalysis.tracks.length > 0) {
            cy.contains('Download').should('be.visible');
          }
        }
      }
    });
  });
});
