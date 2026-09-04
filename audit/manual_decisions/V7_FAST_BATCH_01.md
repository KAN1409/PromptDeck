# V7 Fast Track — Batch 01

Human editorial decisions using the global family analysis as retrieval assistance. These are not automatic similarity decisions.

## Global family decisions

### Code Review
Source family includes Comprehensive Code Review Expert, Code Review Specialist 2, Code Review Professional, Code Review Specialist 3, Code Review Expert, Code Review Specialist, Code Reviewer.
Decision: CONSOLIDATE.
Visible catalog: one canonical **Code Review** capability, with optional modes `Quick`, `Deep`, `PR`, and `Security-aware` only where source instructions support meaningful differences. Preserve the short `/review` command separately as a composable quick command if present.
Canonical design: inspect correctness, maintainability, security/reliability risks, edge cases, tests, and prioritized fixes; cite concrete code locations when available; distinguish defects from suggestions; do not invent runtime behavior.

### Prompt Engineering
Decision: CONSOLIDATE into four user-intent capabilities:
1. **Prompt Generator** — create a prompt from a goal/context.
2. **Prompt Enhancer** — improve an existing prompt.
3. **Prompt Reliability Audit** — identify ambiguity, missing context, conflicting instructions, unverifiable assumptions, and likely failure modes.
4. **Reverse Prompt Engineer** — infer a reusable prompt/specification from an example output.
Concise, clarification-first, token-efficient and format-preserving behaviors become variants/options, not separate top-level cards.
Remove fake expertise years, decorative personas, model/vendor branding, and unsupported autonomy.

### Session Continuity
Decision: CONSOLIDATE Continue & Recap + Context Migration + Session Continuity into one **Session Handoff** family.
Modes: `Continue here`, `Migrate to new chat`, `Compact context`.
Canonical output must separate established context, current state, decisions, constraints, open loops, and next actions. It must not imply hidden memory or fabricate missing history.

### QA / Testing
Decision: CONSOLIDATE Test Engineer / API Tester / Test Analyzer / Quality Engineering and overlapping technical QA prompts into **Testing & QA** family.
Modes: `Test strategy`, `Generate cases`, `API tests`, `Analyze failures`, `Regression`, `Release audit`.
Keep `/tests` as a quick composable command if present.

### SEO
Decision: split by genuinely different user outcome, not agent persona:
- **SEO Audit** — diagnose technical/content/on-page issues.
- **SEO Optimize** — improve a supplied page/content against target intent/keywords.
Performance tuning is NOT an SEO variant and moves to Technical Performance.

### Root Cause / Debugging
Decision: retain **Root Cause Analysis** as a deep diagnostic capability distinct from quick `/debug` and `/fix` commands.
Bug Risk Analyst and Error Handler merge only where they add diagnostic checks; generic role wording is removed.

### Product / Project Management
PRD, Project Manager, Act as a Product Manager, Product Manager are NOT one duplicate family despite similarity clustering.
Decision:
- **PRD Builder** remains a distinct deliverable capability.
- **Project Planner/Manager** remains a planning/execution capability if its source adds reusable planning behavior.
- generic `Act as Product Manager` persona cards merge/remove unless they add a distinct workflow.
This corrects an over-cluster from the embedding analysis.

## Image families — grouping policy corrections

The embedding analysis over-grouped visually different prompts. Treat broad style words as facets, not proof of duplication.

### Surreal family
`BoldSurrealInteriors`, `SurrealUnderwaterPortrait`, `SurrealPrimaryStillLife`, `AbstractArtisticSilhouette`, `SurrealistCastleCloudscape`, `SurrealistWaterComposition`, `SurrealCircularOceanView`, `AbstractGeometricSurrealism`, `SurrealVibrantFantasy`, `SurrealDoubleExposurePortrait`, `AbstractSurrealPortrait` remain meaningful visual variants under a discoverable **Surreal** collection/facet. Do NOT collapse to one prompt.

### Ethereal family
Nature portrait, ink dynamics, floral film, water portrait, underwater portrait and pastel landscape are meaningful treatment/subject variants. Group for navigation, retain distinct variants.

### Everyday candid scenes
Museum steps, rooftop sunset, rainy street, neon alley, nightclub booth, tech desk, restaurant candle, minimal studio candid, blue-hour bridge; and kitchen/bookstore/balcony/subway/farmers-market scenes are not duplicates. Reclassify from Specialist Roles to Photo/Image > Lifestyle/Candid scenes and expose scene/location facets.

### Background editing
`BackgroundReplacement` is canonical capability. Pure white and green-gradient replacements become presets/variants. `CleanProductShotOnWhiteBackground` remains distinct because it is a product-photography outcome, not merely background replacement.

### Floral fantasy
Exaggerated Vibrant Floral Fantasy, Floral Fantasy, Vibrant Fantasy and Vibrant Floral are candidates for one **Floral Fantasy Portrait** family with intensity/style variants; preserve genuinely different composition instructions.

### Dramatic monochrome / spotlight portraits
Keep a shared **Dramatic Portrait Lighting** family only if full prompt comparison confirms same outcome. Monochrome vs spotlight are meaningful facets/variants and must not be blindly deleted.

## Immediate removals / demotions
- `Good for us`, `Drunk Woman`, `Abandoned Wife`, `Lonely cry`: similarity grouping is semantically poor; review as individual one-off image/story requests. Default REMOVE from top-level catalog unless full prompt reveals a reusable transformation workflow.
- One-off named-project/product briefs remain removal candidates; salvage reusable methodology into an existing canonical capability when valuable.
- Vendor/model-specific agent wrappers remain removal/rewrite candidates unless generalized behavior is valuable for ChatGPT.

## Fast-track rule
From this batch onward, global clustering is used to surface families, while human review explicitly corrects both false merges and missed merges. A family may yield one canonical card, multiple meaningful variants, or multiple distinct capabilities.
