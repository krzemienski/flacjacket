#!/bin/bash

# Define colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Define base URL
BASE_URL="http://localhost:5001/api"

# SoundCloud URLs to test
SOUNDCLOUD_URLS=(
    "https://soundcloud.com/soundnightclub/sparrow-barbossa-live-at-sound-on-031624"
    "https://soundcloud.com/sweetmusicofc/sweet-mixtape-135-sparrow-barbossa"
    "https://soundcloud.com/sparrowandbarbossa/maggies1"
)

# Function to print test status
print_status() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✓ PASS${NC}: $2"
    else
        echo -e "${RED}✗ FAIL${NC}: $2"
        exit 1
    fi
}

# Check if the API is running
echo -e "${YELLOW}Testing if API is running...${NC}"
HEALTH_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" ${BASE_URL}/health)
if [ "$HEALTH_RESPONSE" -eq 200 ]; then
    print_status 0 "API is running"
else
    print_status 1 "API is not running. Got HTTP code: $HEALTH_RESPONSE"
fi

# Array to store analysis IDs
declare -a ANALYSIS_IDS

# Test each SoundCloud URL
for url in "${SOUNDCLOUD_URLS[@]}"; do
    echo -e "\n${YELLOW}Testing URL: ${url}${NC}"
    
    # 1. Create analysis
    echo -e "${YELLOW}Creating analysis...${NC}"
    ANALYSIS_RESPONSE=$(curl -s -X POST ${BASE_URL}/analysis \
        -H "Content-Type: application/json" \
        -d "{\"url\": \"${url}\"}")
    
    ANALYSIS_ID=$(echo $ANALYSIS_RESPONSE | jq -r '.id')
    RESPONSE_URL=$(echo $ANALYSIS_RESPONSE | jq -r '.url')
    
    if [ "$RESPONSE_URL" = "$url" ]; then
        print_status 0 "Analysis created with ID: $ANALYSIS_ID"
        ANALYSIS_IDS+=("$ANALYSIS_ID")
    else
        print_status 1 "Failed to create analysis for URL: $url"
    fi
    
    # 2. Check initial status
    echo -e "${YELLOW}Checking initial status...${NC}"
    STATUS_RESPONSE=$(curl -s -X GET ${BASE_URL}/analysis/${ANALYSIS_ID})
    
    INITIAL_STATUS=$(echo $STATUS_RESPONSE | jq -r '.status')
    if [[ $INITIAL_STATUS == "pending" || $INITIAL_STATUS == "processing" ]]; then
        print_status 0 "Initial status: $INITIAL_STATUS"
    else
        print_status 1 "Unexpected initial status: $INITIAL_STATUS"
    fi
    
    # 3. Wait for processing to start (optional)
    echo -e "${YELLOW}Waiting for processing to start...${NC}"
    for i in {1..30}; do
        STATUS_RESPONSE=$(curl -s -X GET ${BASE_URL}/analysis/${ANALYSIS_ID})
        CURRENT_STATUS=$(echo $STATUS_RESPONSE | jq -r '.status')
        
        if [[ $CURRENT_STATUS != "pending" ]]; then
            print_status 0 "Processing started: $CURRENT_STATUS"
            break
        fi
        
        if [ $i -eq 30 ]; then
            print_status 1 "Timeout waiting for processing to start"
        fi
        
        sleep 1
    done
done

# Wait for analyses to complete (within a timeout period)
echo -e "\n${YELLOW}Waiting for analyses to complete...${NC}"
TIMEOUT=300  # 5 minutes
START_TIME=$(date +%s)

for id in "${ANALYSIS_IDS[@]}"; do
    echo -e "${YELLOW}Waiting for analysis ID: ${id}${NC}"
    
    while true; do
        CURRENT_TIME=$(date +%s)
        ELAPSED_TIME=$((CURRENT_TIME - START_TIME))
        
        if [ $ELAPSED_TIME -gt $TIMEOUT ]; then
            print_status 1 "Timeout waiting for analysis to complete"
            break
        fi
        
        STATUS_RESPONSE=$(curl -s -X GET ${BASE_URL}/analysis/${id})
        CURRENT_STATUS=$(echo $STATUS_RESPONSE | jq -r '.status')
        
        if [[ $CURRENT_STATUS == "completed" ]]; then
            # Check tracks
            TRACKS=$(echo $STATUS_RESPONSE | jq '.tracks | length')
            print_status 0 "Analysis completed with $TRACKS tracks detected"
            break
        elif [[ $CURRENT_STATUS == "failed" ]]; then
            ERROR_MSG=$(echo $STATUS_RESPONSE | jq -r '.error_message')
            print_status 1 "Analysis failed: $ERROR_MSG"
            break
        fi
        
        echo -e "${YELLOW}Status: ${CURRENT_STATUS}, waiting...${NC}"
        sleep 5
    done
done

# Check final state of all analyses
echo -e "\n${YELLOW}Checking final state of all analyses...${NC}"
for id in "${ANALYSIS_IDS[@]}"; do
    STATUS_RESPONSE=$(curl -s -X GET ${BASE_URL}/analysis/${id})
    FINAL_STATUS=$(echo $STATUS_RESPONSE | jq -r '.status')
    TRACKS=$(echo $STATUS_RESPONSE | jq '.tracks | length')
    
    if [[ $FINAL_STATUS == "completed" ]]; then
        print_status 0 "Analysis ID $id: $FINAL_STATUS with $TRACKS tracks"
    else
        print_status 1 "Analysis ID $id: $FINAL_STATUS"
    fi
done

# List all analyses to verify
echo -e "\n${YELLOW}Listing all analyses...${NC}"
LIST_RESPONSE=$(curl -s -X GET ${BASE_URL}/analysis)
TOTAL_ANALYSES=$(echo $LIST_RESPONSE | jq '.analyses | length')

print_status 0 "Total analyses: $TOTAL_ANALYSES"

echo -e "\n${GREEN}✓ All SoundCloud URL tests passed${NC}"
exit 0
