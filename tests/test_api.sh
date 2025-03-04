#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

# Check if running in Docker network
if ping -c 1 backend &> /dev/null; then
  # Inside Docker network
  BASE_URL="http://backend:5000/api"
else
  # Outside Docker network (running from host)
  BASE_URL="http://localhost:5001/api"
fi

# Verified working SoundCloud URLs
TEST_URL="https://soundcloud.com/sparrowandbarbossa/maggies1"

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

echo "Using API URL: $BASE_URL"

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
    -d "{\"url\": \"${TEST_URL}\"}")

if [ $? -eq 0 ] && [ "$(echo $ANALYSIS_RESPONSE | jq -r '.url')" = "${TEST_URL}" ]; then
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
    STATUS=$(echo $STATUS_RESPONSE | jq -r '.status')
    if [[ $STATUS == "pending" || $STATUS == "processing" || $STATUS == "completed" ]]; then
        print_result 0 "Get Analysis Status: Status is $STATUS"
    else
        print_result 1 "Get Analysis Status: Invalid status - $STATUS"
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
    if [ $? -eq 0 ]; then
        print_result 0 "Deleted analysis successfully"
    else
        print_result 1 "Failed to delete analysis"
        echo "Response: $DELETE_RESPONSE"
    fi
fi

echo "================================"
echo "Tests completed: $((TESTS_PASSED + TESTS_FAILED))"
echo "Tests passed: $TESTS_PASSED"
echo "Tests failed: $TESTS_FAILED"

# Exit with error code if any tests failed
if [ $TESTS_FAILED -gt 0 ]; then
    exit 1
fi

exit 0
