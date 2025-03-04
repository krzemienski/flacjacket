#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Project root directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo -e "${YELLOW}Starting all FlacJacket tests...${NC}"
echo "==========================================="

# Run API tests
echo -e "${YELLOW}Running API tests...${NC}"
cd "$PROJECT_ROOT"
if ./tests/test_api.sh; then
  echo -e "${GREEN}✓ API tests passed${NC}"
  API_TESTS_PASSED=true
else
  echo -e "${RED}✗ API tests failed${NC}"
  API_TESTS_PASSED=false
fi

echo ""

# Run frontend Cypress tests
echo -e "${YELLOW}Running frontend tests...${NC}"
cd "$PROJECT_ROOT/frontend"

# Check if Cypress is installed
if ! [ -x "$(command -v npx)" ]; then
  echo -e "${RED}Error: npx is not installed. Please install Node.js and npm.${NC}" >&2
  exit 1
fi

# Make sure to install dependencies first if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
  echo "Installing frontend dependencies..."
  npm install
fi

# Run Cypress tests
if npx cypress run; then
  echo -e "${GREEN}✓ Frontend tests passed${NC}"
  FRONTEND_TESTS_PASSED=true
else
  echo -e "${RED}✗ Frontend tests failed${NC}"
  FRONTEND_TESTS_PASSED=false
fi

echo ""

# Run SoundCloud URL tests
echo -e "${YELLOW}Running SoundCloud URL tests...${NC}"
cd "$PROJECT_ROOT"
if ./tests/test_soundcloud_urls.sh; then
  echo -e "${GREEN}✓ SoundCloud URL tests passed${NC}"
  SOUNDCLOUD_TESTS_PASSED=true
else
  echo -e "${RED}✗ SoundCloud URL tests failed${NC}"
  SOUNDCLOUD_TESTS_PASSED=false
fi

echo ""
echo "==========================================="

# Check overall test status
if [ "$API_TESTS_PASSED" = true ] && [ "$FRONTEND_TESTS_PASSED" = true ] && [ "$SOUNDCLOUD_TESTS_PASSED" = true ]; then
  echo -e "${GREEN}All tests passed!${NC}"
  exit 0
else
  echo -e "${RED}Some tests failed. Check logs above for details.${NC}"
  exit 1
fi
