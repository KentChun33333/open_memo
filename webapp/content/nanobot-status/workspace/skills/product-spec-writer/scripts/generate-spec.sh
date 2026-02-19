#!/bin/bash
# generate-spec.sh - Generate product specification from natural language input

set -e

# Input: Product description (passed as argument or stdin)
INPUT="${1:-$(cat)}"

if [ -z "$INPUT" ]; then
    echo "Usage: $0 <product-description>"
    echo "Or pipe input: echo 'product description' | $0"
    exit 1
fi

# Output directory
OUTPUT_DIR="${OUTPUT_DIR:-.}"
OUTPUT_FILE="$OUTPUT_DIR/product-spec.md"

# Templates directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEMPLATE_DIR="$SCRIPT_DIR/../../skills/product-spec-writer/templates"

# Select template based on product type (simple heuristic)
select_template() {
    local input_lower=$(echo "$INPUT" | tr '[:upper:]' '[:lower:]')
    
    if [[ "$input_lower" == *"web"* ]] || [[ "$input_lower" == *"website"* ]]; then
        echo "$TEMPLATE_DIR/web-app.md"
    elif [[ "$input_lower" == *"mobile"* ]] || [[ "$input_lower" == *"app"* ]]; then
        echo "$TEMPLATE_DIR/mobile-app.md"
    elif [[ "$input_lower" == *"saas"* ]] || [[ "$input_lower" == *"platform"* ]]; then
        echo "$TEMPLATE_DIR/saas-platform.md"
    else
        echo "$TEMPLATE_DIR/web-app.md"  # Default
    fi
}

TEMPLATE_FILE=$(select_template)

if [ ! -f "$TEMPLATE_FILE" ]; then
    echo "Error: Template not found: $TEMPLATE_FILE"
    exit 1
fi

# Generate specification
echo "Generating product specification..."
echo "Input: $INPUT"
echo "Template: $TEMPLATE_FILE"
echo ""

# Create the specification (this would normally call an LLM or parsing logic)
cat > "$OUTPUT_FILE" << EOF
# Product Specification

## Product Overview
**Product Type**: $(echo "$INPUT" | grep -oP '(web|mobile|saas|platform)' | head -1 | tr '[:upper:]' '[:lower:]' | xargs -I {} echo -n "Web Application" 2>/dev/null || echo "Custom Application")
**Generated**: $(date +%Y-%m-%d)
**Input Description**: $INPUT

## Features and Requirements
This specification is based on the provided input. For a comprehensive spec, please provide:
- Target users and personas
- Core functionality requirements
- Technical constraints
- Timeline and milestones
- Success metrics

## Technical Considerations
- Platform requirements
- API integrations
- Security and compliance
- Scalability needs

## Next Steps
1. Review and validate requirements
2. Create detailed user stories
3. Design UI/UX wireframes
4. Plan technical architecture
5. Establish success metrics

## Output Location
Specification saved to: $OUTPUT_FILE
EOF

echo "Specification generated successfully!"
echo "Output: $OUTPUT_FILE"