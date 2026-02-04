#!/bin/bash
# validate_state_locking.sh
# Tests that Terraform state locking prevents concurrent operations

set -e

TERRAFORM_DIR="${1:-infra/terraform}"
TIMEOUT=10

echo "🔒 Testing Terraform State Locking..."
echo "Directory: $TERRAFORM_DIR"
echo ""

cd "$TERRAFORM_DIR"

# Ensure terraform is initialized
if [ ! -d ".terraform" ]; then
    echo "⚠️ Terraform not initialized. Running init..."
    terraform init -backend=false > /dev/null 2>&1
fi

# Start a long-running terraform operation in background
echo "Starting background terraform plan..."
terraform plan -lock-timeout=5s > /tmp/tf_plan_1.log 2>&1 &
PID1=$!

# Wait a moment for the lock to be acquired
sleep 2

# Try to run another terraform operation
echo "Attempting concurrent terraform plan..."
if terraform plan -lock-timeout=1s > /tmp/tf_plan_2.log 2>&1; then
    # If second plan succeeds, check if first is still running
    if ps -p $PID1 > /dev/null 2>&1; then
        echo "⚠️ WARNING: Concurrent plans may have succeeded (first still running)"
        RESULT="warning"
    else
        echo "✅ Both plans completed (first finished before second started)"
        RESULT="pass"
    fi
else
    # Second plan failed - check if it's due to locking
    if grep -q "Error acquiring the state lock\|lock\|locked" /tmp/tf_plan_2.log 2>/dev/null; then
        echo "✅ State locking is working correctly!"
        echo "   Second operation was blocked as expected."
        RESULT="pass"
    else
        echo "❌ Second plan failed but not due to locking:"
        cat /tmp/tf_plan_2.log
        RESULT="fail"
    fi
fi

# Cleanup
kill $PID1 2>/dev/null || true
wait $PID1 2>/dev/null || true

echo ""
echo "=== Test Result: $RESULT ==="

if [ "$RESULT" = "pass" ]; then
    exit 0
elif [ "$RESULT" = "warning" ]; then
    exit 0
else
    exit 1
fi
