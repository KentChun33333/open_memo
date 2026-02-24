---
name: product-spec-writer
description: Create comprehensive product specifications for web, mobile, and desktop applications. Use when the agent needs to generate detailed product specs including requirements, architecture, UI/UX guidance, and success metrics for software products.
---

# Product Specification Writer

This skill helps create comprehensive product specifications for web, mobile, and desktop applications, following industry best practices.

## Quick Start

Generate a product spec by providing:
- **Product type**: web app, mobile app, desktop app, or SaaS platform
- **Key features**: 3-5 core features
- **Target audience**: primary users and their needs

## Usage

### Input Parameters

1. **Product type** (required): `web-app`, `mobile-app`, `desktop-app`, `saas-platform`
2. **Key features** (required): List of 3-5 core features
3. **Target audience** (required): Describe primary users and their needs
4. **Additional requirements** (optional): Technical constraints, compliance needs, etc.

### Output Format

The generated spec includes:
- Executive summary
- User requirements & user stories
- Functional requirements
- Non-functional requirements
- Technical architecture
- UI/UX guidance
- Success metrics & KPIs
- Timeline & milestones

### Scripts

- `scripts/generate-spec.sh` - Generate a new spec (see below)
- `scripts/validate-spec.sh` - Validate spec completeness

## Scripts

### generate-spec.sh

Generates a product specification based on parameters.

```bash
# Basic usage
./scripts/generate-spec.sh --type web-app --features "user-auth,real-time-data,analytics" --audience "marketing-team" --output spec.md

# With additional requirements
./scripts/generate-spec.sh --type mobile-app --features "push-notifications,offline-mode,location" --audience "field-sales-team" --requirements "iOS-15+,Android-12+" --output mobile-spec.md
```

Flags:
- `--type` (required): Product type (web-app, mobile-app, desktop-app, saas-platform)
- `--features` (required): Comma-separated list of key features
- `--audience` (required): Target audience description
- `--requirements` (optional): Additional requirements
- `--output` (optional): Output file path (defaults to stdout)

## Templates

Select the appropriate template based on product type:

- `templates/web-app.md` - For browser-based applications
- `templates/mobile-app.md` - For iOS and Android applications  
- `templates/saas-platform.md` - For subscription-based software platforms

Each template includes sections for requirements, architecture, UI/UX, and success metrics.

## Example Scenarios

### Scenario 1: Internal Dashboard
```
User: "Create a product spec for an internal analytics dashboard for our sales team"
Parameters:
  type: web-app
  features: "data-visualization,sales-forecasting,team-performance"
  audience: "sales-managers-and-representatives"
```

### Scenario 2: Mobile Field App
```
User: "Create a spec for a mobile app for our field technicians"
Parameters:
  type: mobile-app
  features: "work-order-management,inventory-scanning,offline-sync"
  audience: "field-technicians"
```

### Scenario 3: SaaS Platform
```
User: "Create a spec for a project management SaaS for remote teams"
Parameters:
  type: saas-platform
  features: "task-management,team-collaboration,client-portals"
  audience: "project-managers-and-team-leaders"
```

## Best Practices

1. **Be specific about features** - Clear feature lists lead to better specifications
2. **Define success metrics early** - This helps guide design decisions
3. **Consider non-functional requirements** - Performance, security, and scalability matter
4. **Include user stories** - They ensure the product addresses real user needs

## When to Use

Use this skill when you need to:
- Create product specifications for new development projects
- Document requirements for existing products
- Prepare project documentation for stakeholders
- Guide UI/UX design decisions with clear requirements
