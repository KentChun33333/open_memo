#!/bin/bash

# Product Specification Generator
# Generates comprehensive product specs based on input parameters
# Usage: ./generate-spec.sh --type <type> --features <features> --audience <audience> [--requirements <reqs>] [--output <file>]

set -e

# Parse arguments
TYPE=""
FEATURES=""
AUDIENCE=""
REQUIREMENTS=""
OUTPUT=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --type)
            TYPE="$2"
            shift 2
            ;;
        --features)
            FEATURES="$2"
            shift 2
            ;;
        --audience)
            AUDIENCE="$2"
            shift 2
            ;;
        --requirements)
            REQUIREMENTS="$2"
            shift 2
            ;;
        --output)
            OUTPUT="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Validate required arguments
if [[ -z "$TYPE" ]]; then
    echo "Error: --type is required (web-app, mobile-app, desktop-app, saas-platform)"
    exit 1
fi

if [[ -z "$FEATURES" ]]; then
    echo "Error: --features is required (comma-separated list)"
    exit 1
fi

if [[ -z "$AUDIENCE" ]]; then
    echo "Error: --audience is required"
    exit 1
fi

# Validate type
case "$TYPE" in
    web-app|mobile-app|desktop-app|saas-platform) ;;
    *)
        echo "Error: Invalid type '$TYPE'. Must be: web-app, mobile-app, desktop-app, saas-platform"
        exit 1
        ;;
esac

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEMPLATE_DIR="$SCRIPT_DIR/../templates"
SKILL_DIR="$SCRIPT_DIR/.."

# Select template
TEMPLATE_FILE="$TEMPLATE_DIR/${TYPE}.md"

if [[ ! -f "$TEMPLATE_FILE" ]]; then
    echo "Error: Template not found for type '$TYPE': $TEMPLATE_FILE"
    exit 1
fi

# Parse features into a readable list
FEATURES_LIST=$(echo "$FEATURES" | tr ',' '\n' | sed 's/^[[:space:]]*//;s/[[:space:]]*$//' | while read feature; do
    echo "- **$feature**"
done | tr '\n' ' ')

# Parse requirements if provided
if [[ -n "$REQUIREMENTS" ]]; then
    REQUIREMENTS_LIST=$(echo "$REQUIREMENTS" | tr ',' '\n' | sed 's/^[[:space:]]*//;s/[[:space:]]*$//' | while read req; do
        echo "- $req"
    done)
else
    REQUIREMENTS_LIST=""
fi

# Generate timestamp
TIMESTAMP=$(date "+%Y-%m-%d %H:%M:%S")

# Read template
TEMPLATE_CONTENT=$(cat "$TEMPLATE_FILE")

# Create a temporary file for processing
TEMP_FILE=$(mktemp)

# Replace placeholders in template
cat "$TEMPLATE_FILE" | sed \
    -e "s/\${PRODUCT_TYPE}/$TYPE/g" \
    -e "s/\${FEATURES}/$FEATURES_LIST/g" \
    -e "s/\${TARGET_AUDIENCE}/$AUDIENCE/g" \
    -e "s/\${ADDITIONAL_REQUIREMENTS}/$REQUIREMENTS_LIST/g" \
    -e "s/\${TIMESTAMP}/$TIMESTAMP/g" \
    > "$TEMP_FILE"

# Output result
if [[ -n "$OUTPUT" ]]; then
    cp "$TEMP_FILE" "$OUTPUT"
    echo "Product spec generated successfully: $OUTPUT"
else
    cat "$TEMP_FILE"
fi

# Cleanup
rm "$TEMP_FILE"
