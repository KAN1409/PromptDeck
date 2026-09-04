# V7 Fast Track — Batch 02

Human editorial decisions on global families surfaced by PROMPT_FAMILY_ANALYSIS_V3. Clustering is retrieval assistance only; false merges are corrected manually.

## High-confidence consolidation

### Cold Email
Reply-Focused Cold Email Builder + PDF Cold outreach email + PDF Cold email -> one canonical **Cold Email** capability.
Keep outcome modes only where useful: `Get a reply`, `Introduce`, `Follow-up`.
Canonical should ask for recipient/context/value proposition/CTA when absent, write concise personalized copy, avoid fabricated familiarity or claims, and provide subject line when appropriate.

### Professional Email
emails Professionals + Professional Email Writer for Any Occasion + Write an Email -> one **Professional Email** family.
Modes: `New email`, `Reply`, `Short`, `Firm`, `Warm professional`.
Cross-reference with `/FirmNotRude` and `/WarmProfessional`; those may remain reusable tone commands rather than duplicate email cards.

### Repository Understanding
Git Repository Analysis and Knowledge Base Construction + GitHub Repository Analysis and Enhancement + Deep GitHub Repository Understanding -> **Repository Understanding** canonical.
Separate modes: `Understand`, `Audit`, `Create knowledge map`. Do not promise repository access unless content/tool access is actually available.
Cross-reference with Codebase Recon from earlier passes.

### Repository Audit & Remediation
Comprehensive Repository Audit & Remediation + Comprehensive Repository Analysis and Bug Fixing Framework -> one deep **Repository Audit** capability. Keep distinct from Repository Understanding because it targets defects/remediation rather than comprehension.

### Prompt Engineering Expert
Prompt Engineering Expert + Prompt Architect Pro -> merge into previously established Prompt Enhancer / Prompt Generator architecture. No standalone expert-persona card.

### App Store Review
Apple App Store Review Compliance Agent + App Store Submission Agent -> **App Store Readiness Review** canonical, with `Compliance review` and `Submission checklist` modes.

### Exam Tutor
AI Exam Mastery Tutor + Personalized Exam Preparation Tutor -> **Adaptive Exam Tutor** canonical. Subject/model branding becomes input/facet, not separate card.

### Investigative Research
Investigative Research Assistant + non-mainstream variant -> one **Investigative Research** family. The non-mainstream option becomes a mode requiring source-quality checks and explicit distinction between established evidence, disputed claims, and speculation.

### Literature Reading
Literature Reading Assistant + Literature Reading and Analysis Assistant -> one **Literature Reading & Analysis** capability. Keep separate from Literature Gap Finder because reading/analysis and gap discovery have different outcomes.

### Birthday Messages
Birthday Message Generator – 3 Styles + Customizable Birthday Message Generator -> one **Birthday Message** capability with style variants.

### Dual-Language Semantic Compression
DiComPress Ω + DiComPress -> one **Bilingual Semantic Compression** capability if full prompt preserves meaning across both languages. Remove branded/gimmicky naming; keep language pair as input.

## Correct false merges / split capabilities

### Refactor vs Format
Refactoring Expert and Code Formatter are related but distinct.
- **Refactor Code** changes structure/design while preserving behavior.
- **Format Code** changes presentation/style without semantic redesign.
Keep `/refactor` quick command; formatting can be a lightweight mode/command if not already covered.

### Documentation vs API Design
Documentation Maintainer and API Design Expert are NOT variants. Keep separate canonical capabilities: **Technical Documentation** and **API Design**.

### Vulnerability Audit vs Post-Implementation Audit
Not duplicates.
- **Security/Vulnerability Audit**: threat/security weaknesses.
- **Implementation Audit**: correctness, completeness, regression, maintainability after change.
Can share facets but remain separate outcomes.

### UI Architecture vs System Architecture
Not duplicates. UI architecture belongs frontend/product interface structure; system architecture covers system-level components/data/integration/deployment. Keep separate, cross-link via Architecture facet.

### Database Architecture vs Caching Architecture
Not duplicates. Keep **Database Design/Architecture** and **Caching Strategy** as distinct technical capabilities.

### Multilingual Writing Improvement vs Chinese-English Translation
Not duplicates. One improves writing quality across languages; the other translates. Keep separate families. Translation language pair becomes facet/input.

### Frontend Developer vs React/Next.js Specialist
Generic frontend capability and framework-specific implementation should not create many top-level personas. Canonical **Frontend Development** with framework facet/variant (`React/Next.js`) unless full source provides a materially distinct architecture workflow.

## Image-family decisions

### Mirror Selfie
Photorealistic Mirror Selfie Analysis + Aesthetic Mirror Selfie + Detailed Image Analysis of Mirror Selfie -> navigation family **Mirror Selfie**. Preserve distinct operations: `Analyze reference` vs `Generate/style`. Do not merge analysis and generation into one ambiguous prompt.

### Editorial Beauty ethnicity variants
European / Turkish / East Asian versions -> one **Minimal Editorial Beauty** visual treatment. Ethnicity is subject input, not a separate prompt card. Canonical must preserve the supplied subject's identity/ethnicity rather than defaulting to a preset ethnicity.

### Double Exposure Portrait
Nature / Vibrant / Color variants -> one **Double Exposure Portrait** family with composition/color variants, unless full prompt shows materially different techniques.

### Cinematic Noir portraits
Window / nighttime urban / lake are scene variants under cinematic portrait discovery; retain location/lighting variants rather than deleting them.

### African portrait styles
Indigenous dusk / African art / vibrant documentary are not automatically duplicates. Retain as distinct style/context variants where culturally and visually meaningful; avoid collapsing culturally specific treatments into a generic style card.

### Ankara / Turkish scene clusters
Most are scene-generation recipes, not Research/Specialist capabilities. Move to Photo/Image > Lifestyle/Cinematic scenes. Similar location alone is not duplication. Remove only truly one-off low-reusability scenes after full-text check.

## Remove / exclude from general catalog

- Stake.us dice wagering strategy prompts -> REMOVE from PromptDeck general catalog.
- WordPilot-specific Lead Generator & Tracker variant -> remove vendor-specific wrapper; keep a general Lead Generation/Tracking capability only if useful content survives.
- Prompt Generator for Claude Code -> merge only general prompt-generation methodology; vendor-specific card removed.
- SABARUDIN named frameworks -> remove as standalone cards unless a clearly reusable methodology survives after debranding.
- Video/HUD/8K entries branded to a named agent/designer -> debrand and move only genuinely useful visual recipes to Image; otherwise remove.
- malformed/generic `Digital product ideas / Sales / Selar ideas for automation` cluster -> do not merge blindly. Keep **Digital Product Ideas** only if prompt quality/usefulness warrants it; generic Sales and platform-specific Selar entry are separate/low-value candidates.

## Cross-reference notes

1. Email hierarchy should become `Email` capability + purpose/tone facets, not dozens of title variants.
2. Technical architecture uses domain facets (`System`, `UI`, `Database`, `Cache`, `Frontend`) but domains with materially different reasoning remain distinct canonical capabilities.
3. Image analysis and image generation must remain separate intents even when the subject/style words are nearly identical.
4. Location, ethnicity, programming framework, language pair, and model name should usually be facets/inputs, not reasons to create duplicate top-level cards.
5. Safety/quality: do not preserve prompts whose core purpose is gambling optimization; do not retain vendor/model-specific behavior claims as if ChatGPT supports them.
