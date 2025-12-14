#!/bin/bash

# Test runner script for Discord Finance Bot

echo "========================================"
echo "Discord Finance Bot - Test Suite"
echo "========================================"
echo ""

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    echo "⚠️  pytest is not installed. Installing..."
    pip install -r requirements-dev.txt
    echo ""
fi

# Run all tests
echo "🧪 Running all tests..."
echo ""
pytest tests/ -v

# Check exit code
if [ $? -eq 0 ]; then
    echo ""
    echo "========================================"
    echo "✅ All tests passed!"
    echo "========================================"
else
    echo ""
    echo "========================================"
    echo "❌ Some tests failed!"
    echo "========================================"
    exit 1
fi
