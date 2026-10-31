#!/bin/bash

# Test script for Scorebox Data API
# Usage: ./test-api.sh [base_url]
# Example: ./test-api.sh http://localhost:8484
# Example: ./test-api.sh https://scorebox-data.fluin.io

BASE_URL=${1:-http://localhost:8484}

echo "======================================"
echo "Testing Scorebox Data API"
echo "Base URL: $BASE_URL"
echo "======================================"
echo ""

# Test 1: Health Check
echo "1. Testing Health Check..."
echo "GET $BASE_URL/health"
curl -s "$BASE_URL/health" | python3 -m json.tool
echo ""
echo ""

# Test 2: Root Endpoint
echo "2. Testing Root Endpoint..."
echo "GET $BASE_URL/"
curl -s "$BASE_URL/" | python3 -m json.tool
echo ""
echo ""

# Test 3: Get Score for MIN (Minnesota Wild)
echo "3. Testing Score Endpoint (MIN)..."
echo "GET $BASE_URL/api/scores/MIN"
curl -s "$BASE_URL/api/scores/MIN" | python3 -m json.tool
echo ""
echo ""

# Test 4: Get Score for CHI (Chicago Blackhawks)
echo "4. Testing Score Endpoint (CHI)..."
echo "GET $BASE_URL/api/scores/CHI"
curl -s "$BASE_URL/api/scores/CHI" | python3 -m json.tool
echo ""
echo ""

# Test 5: Post a Log Event
echo "5. Testing Log Event (POST)..."
echo "POST $BASE_URL/api/log"
curl -s -X POST "$BASE_URL/api/log" \
  -H "Content-Type: application/json" \
  -d '{
    "deviceId": "test-device-001",
    "hostname": "test-scorebox",
    "eventName": "test_event",
    "eventDetails": "API test from shell script"
  }' | python3 -m json.tool
echo ""
echo ""

# Test 6: Get Log Events
echo "6. Testing Get Logs..."
echo "GET $BASE_URL/api/log?limit=5"
curl -s "$BASE_URL/api/log?limit=5" | python3 -m json.tool
echo ""
echo ""

echo "======================================"
echo "Testing Complete!"
echo "======================================"
