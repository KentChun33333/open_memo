#!/bin/bash
# Daily Wealth & Blog Summary - Runs at 7:30 AM SGT
# Target: $2M → $30M + Physical Assets

BLOG_DIR="/Users/kentchiu/.nanobot/workspace/openmemo/webapp/content/blogs"
MEMORY_DIR="/Users/kentchiu/.nanobot/workspace/memory"
DATE_TODAY=$(date +%Y-%m-%d)
DATE_YESTERDAY=$(date -v-1d +%Y-%m-%d 2>/dev/null || date -d "yesterday" +%Y-%m-%d)
OUTPUT_FILE="$MEMORY_DIR/daily-summary-$(date +%Y-%m-%d).md"

# Calculate yesterday's date in the correct format
YEAR=$(date +%Y)
MONTH=$(date +%m)
DAY=$(date +%d)
DAY=$((DAY - 1))
if [ $DAY -lt 1 ]; then
    MONTH=$((MONTH - 1))
    if [ $MONTH -lt 1 ]; then
        MONTH=12
        YEAR=$((YEAR - 1))
    fi
    DAY=$(cal $MONTH $YEAR | grep -E '^[0-9]+' | tail -1)
fi
DATE_YESTERDAY=$(printf "%04d-%02d-%02d" $YEAR $MONTH $DAY)

echo "=== Daily Wealth & Blog Summary ===" > "$OUTPUT_FILE"
echo "Date: $(date)" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

# Summarize yesterday's blogs
echo "## Yesterday's Blog Summary (${DATE_YESTERDAY})" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

YESTERDAY_BLOG="$BLOG_DIR/${DATE_YESTERDAY}-*.mdx"
if ls $YESTERDAY_BLOG 1> /dev/null 2>&1; then
    for blog in $YESTERDAY_BLOG; do
        if [ -f "$blog" ]; then
            TITLE=$(grep "^title:" "$blog" | sed 's/title: //' | tr -d '"')
            echo "### ${TITLE}" >> "$OUTPUT_FILE"
            echo "" >> "$OUTPUT_FILE"
            # Extract and summarize content (first 200 words)
            CONTENT=$(grep -A 100 "^---" "$blog" | tail -n +2 | head -200)
            echo "${CONTENT}..." >> "$OUTPUT_FILE"
            echo "" >> "$OUTPUT_FILE"
        fi
    done
else
    echo "No blogs found for ${DATE_YESTERDAY}" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
fi

# Wealth-building suggestions for today
echo "## Wealth-Building Suggestions (Target: \$2M → \$30M)" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"
echo "### Asset Allocation (Total: \$2M+)" >> "$OUTPUT_FILE"
echo "- **Low-Risk (30%):** \$600K - Bonds, Fixed Income, High-Yield Savings" >> "$OUTPUT_FILE"
echo "- **Equities (50%):** \$1M - Index Funds (SPY/QQQ), Dividend Stocks" >> "$OUTPUT_FILE"
echo "- **Venture Capital (20%):** \$400K - Singapore/Malaysia Startups, Angel Investing" >> "$OUTPUT_FILE"
echo "- **Physical Assets (10-15%):** \$200K-\$300K - Real Estate, Gold, Collectibles" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

echo "### Today's Action Items" >> "$OUTPUT_FILE"
echo "1. **Review Portfolio:** Check asset allocation vs. target" >> "$OUTPUT_FILE"
echo "2. **SIP Investment:** Execute automated equity investments" >> "$OUTPUT_FILE"
echo "3. **Network:** Connect with 1 Singapore entrepreneur/VC" >> "$OUTPUT_FILE"
echo "4. **SaaS Development:** Dedicate 2 hours to compliance tool MVP" >> "$OUTPUT_FILE"
echo "5. **Learning:** Read one article on MAS-regulated fintech" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

echo "### Singapore-Specific Opportunities" >> "$OUTPUT_FILE"
echo "- CPF OA/SA optimization (4% interest)" >> "$OUTPUT_FILE"
echo "- S-REITs for monthly income (5-6% yield)" >> "$OUTPUT_FILE"
echo "- Startup SG Grant for SaaS business" >> "$OUTPUT_FILE"
echo "- SGX ETFs for low-cost equity exposure" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

echo "---" >> "$OUTPUT_FILE"
echo "*Generated daily at 7:30 AM SGT*" >> "$OUTPUT_FILE"

# Display the summary
cat "$OUTPUT_FILE"
