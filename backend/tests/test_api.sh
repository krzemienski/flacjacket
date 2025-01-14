#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

# Base URL
BASE_URL="http://backend:5000/api"

# Test counter
TESTS_PASSED=0
TESTS_FAILED=0

# Function to print test results
print_result() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✓ $2${NC}"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        echo -e "${RED}✗ $2${NC}"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi
}

echo "Starting FlacJacket API Tests..."
echo "================================"

# Test 1: Health Check
echo -n "Testing API Health... "
HEALTH_CHECK=$(curl -s -o /dev/null -w "%{http_code}" ${BASE_URL}/health)
if [ "$HEALTH_CHECK" = "200" ]; then
    print_result 0 "Health check passed"
else
    print_result 1 "Health check failed (Status: $HEALTH_CHECK)"
fi

# Test 2: Create New Analysis
echo -n "Testing Create Analysis... "
ANALYSIS_RESPONSE=$(curl -s -X POST ${BASE_URL}/analysis \
    -H "Content-Type: application/json" \
    -d '{"url": "https://soundcloud.com/example/test-track"}')

if [ $? -eq 0 ] && [ "$(echo $ANALYSIS_RESPONSE | jq -r '.url')" = "https://soundcloud.com/example/test-track" ]; then
    print_result 0 "Analysis created successfully"
    ANALYSIS_ID=$(echo $ANALYSIS_RESPONSE | jq -r '.id')
else
    print_result 1 "Failed to create analysis"
    echo "Response: $ANALYSIS_RESPONSE"
fi

# Test 3: Get Analysis Status
if [ ! -z "$ANALYSIS_ID" ]; then
    echo -n "Testing Get Analysis Status... "
    STATUS_RESPONSE=$(curl -s ${BASE_URL}/analysis/$ANALYSIS_ID)
    if [ $? -eq 0 ] && [ "$(echo $STATUS_RESPONSE | jq -r '.id')" = "$ANALYSIS_ID" ]; then
        print_result 0 "Got analysis status successfully"
    else
        print_result 1 "Failed to get analysis status"
        echo "Response: $STATUS_RESPONSE"
    fi
fi

# Test 4: List Analyses
echo -n "Testing List Analyses... "
LIST_RESPONSE=$(curl -s ${BASE_URL}/analyses)
if [ $? -eq 0 ] && [ "$(echo $LIST_RESPONSE | jq -e '.analyses')" != null ]; then
    print_result 0 "Listed analyses successfully"
else
    print_result 1 "Failed to list analyses"
    echo "Response: $LIST_RESPONSE"
fi

# Test 5: Delete Analysis
if [ ! -z "$ANALYSIS_ID" ]; then
    echo -n "Testing Delete Analysis... "
    DELETE_RESPONSE=$(curl -s -X DELETE ${BASE_URL}/analysis/$ANALYSIS_ID)
    if [ $? -eq 0 ] && [ "$(echo $DELETE_RESPONSE | jq -r '.status')" = "success" ]; then
        print_result 0 "Deleted analysis successfully"
    else
        print_result 1 "Failed to delete analysis"
        echo "Response: $DELETE_RESPONSE"
    fi
fi

# Print summary
echo "================================"
echo "Tests completed: $((TESTS_PASSED + TESTS_FAILED))"
echo "Tests passed: $TESTS_PASSED"
echo "Tests failed: $TESTS_FAILED"

if [ $TESTS_FAILED -eq 0 ]; then
    exit 0
else
    exit 1
fi
