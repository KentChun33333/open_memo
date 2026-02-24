#!/bin/bash
# validate-spec.sh - Validate product specification for completeness and consistency

set -e

SPEC_FILE="${1:-product-spec.md}"

if [ ! -f "$SPEC_FILE" ]; then
    echo "Error: Specification file not found: $SPEC_FILE"
    exit 1
fi

echo "Validating product specification: $SPEC_FILE"
echo ""

VALIDATION_ERRORS=0

# Check for required sections
echo "Checking required sections..."

if ! grep -q "## Product Overview" "$SPEC_FILE"; then
    echo "✗ Missing: Product Overview section"
    VALIDATION_ERRORS=$((VALIDATION_ERRORS + 1))
else
    echo "✓ Product Overview section present"
fi

if ! grep -q "## Features and Requirements" "$SPEC_FILE"; then
    echo "✗ Missing: Features and Requirements section"
    VALIDATION_ERRORS=$((VALIDATION_ERRORS + 1))
else
    echo "✓ Features and Requirements section present"
fi

if ! grep -q "## User Stories" "$SPEC_FILE"; then
    echo "✗ Missing: User Stories section"
    VALIDATION_ERRORS=$((VALIDATION_ERRORS + 1))
else
    echo "✓ User Stories section present"
fi

if ! grep -q "## Technical Architecture" "$SPEC_FILE"; then
    echo "✗ Missing: Technical Architecture section"
    VALIDATION_ERRORS=$((VALIDATION_ERRORS + 1))
else
    echo "✓ Technical Architecture section present"
fi

if ! grep -q "## Success Metrics" "$SPEC_FILE"; then
    echo "✗ Missing: Success Metrics section"
    VALIDATION_ERRORS=$((VALIDATION_ERRORS + 1))
else
    echo "✓ Success Metrics section present"
fi

# Check for acceptance criteria
if ! grep -q "Acceptance Criteria" "$SPEC_FILE" && ! grep -q "AC:" "$SPEC_FILE"; then
    echo "✗ Missing: Acceptance Criteria in user stories"
    VALIDATION_ERRORS=$((VALIDATION_ERRORS + 1))
else
    echo "✓ Acceptance Criteria present"
fi

# Check for user stories count
USER_STORY_COUNT=$(grep -c "^- \[ \]" "$SPEC_FILE" 2>/dev/null || echo "0")
if [ "$USER_STORY_COUNT" -lt 3 ]; then
    echo "⚠ Warning: Fewer than 3 user stories found ($USER_STORY_COUNT)"
else
    echo "✓ User stories count: $USER_STORY_COUNT"
fi

# Summary
echo ""
if [ $VALIDATION_ERRORS -eq 0 ]; then
    echo "✓ Specification validation passed!"
    exit 0
else
    echo "✗ Validation found $VALIDATION_ERRORS error(s)"
    exit 1
fi