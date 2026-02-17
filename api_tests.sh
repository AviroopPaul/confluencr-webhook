#!/usr/bin/env bash
set -euo pipefail

# API test script for the webhook processor.
# Assumes the API is already running.
# Usage:
#   BASE_URL=http://localhost:8000 TXN_ID=txn_123 bash api_tests.sh

BASE_URL=${BASE_URL:-http://localhost:8000}
TXN_ID=${TXN_ID:-txn_$(date +%s)}

payload=$(cat <<JSON
{
  "transaction_id": "$TXN_ID",
  "source_account": "acc_user_789",
  "destination_account": "acc_merchant_456",
  "amount": 1500,
  "currency": "INR"
}
JSON
)

echo "=== 1) Health check: confirms service is up and returns UTC time ==="
curl -i "$BASE_URL/"

echo -e "\n=== 2) Webhook POST (first): expects 202 Accepted + ACK ==="
curl -i -X POST "$BASE_URL/v1/webhooks/transactions" \
  -H "Content-Type: application/json" \
  -d "$payload"

echo -e "\n=== 3) Webhook POST (duplicate): validates idempotency (no duplicate processing) ==="
curl -i -X POST "$BASE_URL/v1/webhooks/transactions" \
  -H "Content-Type: application/json" \
  -d "$payload"

echo -e "\n=== 4) Status GET (immediate): should be PROCESSING right after webhook ==="
curl -i "$BASE_URL/v1/transactions/$TXN_ID"

echo -e "\n=== 5) Wait 31s: ensures background delay has elapsed ==="
sleep 31

echo -e "\n=== 6) Status GET (after delay): should be PROCESSED (or FAILED if error) ==="
curl -i "$BASE_URL/v1/transactions/$TXN_ID"
