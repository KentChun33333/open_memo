#!/bin/bash

# Product Specification Validator
# Validates that a generated spec contains all required sections and is consistent
# Usage: ./validate-spec.sh <spec-file>

set -e

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$SCRIPT_DIR/.."

# Check arguments
if [[ $# -ne 1 ]]; then
    echo "Usage: $0 <spec-file>"
    exit 1
fi

SPEC_FILE="$1"

# Validate file exists
if [[ ! -f "$SPEC_FILE" ]]; then
    echo "Error: Spec file not found: $SPEC_FILE"
    exit 1
fi

# Required sections
REQUIREMENTS=(
    "Executive Summary"
    "User Requirements"
    "Functional Requirements"
    "Non-Functional Requirements"
    "Technical Architecture"
    "UI/UX Guidance"
    "Success Metrics"
    "Timeline"
)

VALIDATION_ERRORS=()
VALIDATION_WARNINGS=()

# Check for required sections
for section in "${REQUIREMENTS[@]}"; do
    if ! grep -iq "$section" "$SPEC_FILE"; then
        VALIDATION_ERRORS+=("Missing section: $section")
    fi
done

# Check for basic consistency
if ! grep -iq "product" "$SPEC_FILE" && ! grep -iq "specification" "$SPEC_FILE"; then
    VALIDATION_WARNINGS+=("No product name or specification title found")
fi

# Check for feature list
if ! grep -iq "feature" "$SPEC_FILE"; then
    VALIDATION_WARNINGS+=("No feature list found")
fi

# Check for audience/requirements
if ! grep -iq "audience\|user\|requirement" "$SPEC_FILE"; then
    VALIDATION_WARNINGS+=("No target audience or user requirements found")
fi

# Check for metrics
if ! grep -iq "metric\|kpi\|success\|measure" "$SPEC_FILE"; then
    VALIDATION_WARNINGS+=("No success metrics found")
fi

# Output results
echo "=== Specification Validation ==="
echo "File: $SPEC_FILE"
echo ""

if [[ ${#VALIDATION_ERRORS[@]} -eq 0 && ${#VALIDATION_WARNINGS[@]} -eq 0 ]]; then
    echo "✓ Validation passed - All required sections present and consistent"
    exit 0
fi

# Output errors
if [[ ${#VALIDATION_ERRORS[@]} -gt 0 ]]; then
    echo "✗ Errors (${#VALIDATION_ERRORS[@]}):"
    for error in "${VALIDATION_ERRORS[@]}"; do
        echo "  - $error"
    done
    echo ""
fi

# Output warnings
if [[ ${#VALIDATION_WARNINGS[@]} -gt 0 ]]; then
    echo "⚠ Warnings (${#VALIDATION_WARNINGS[@]}):"
    for warning in "${VALIDATION_WARNINGS[@]}"; do
        echo "  - $warning"
    done
    echo ""
fi

# Exit with error if there were errors (warnings don't fail validation)
if [[ ${#VALIDATION_ERRORS[@]} -gt 0 ]]; then
    exit 1
fi

exit 0
