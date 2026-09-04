# Human Curation V6 — Pass 05

Scope: Problem Solving & Technical packets 01–03, cross-referenced against technical capabilities already reviewed in AI & Prompting. Human editorial decisions; ChatGPT-first catalog.

## Preserve the core commands

Core GIDs 87 /debug, 88 /fix, 89 /optimize, 113 /edgecases, 114 /refactor, 115 /tests, 116 /security, 86 /check, 90 /better, 107 /rubric, 108 /score are strong compact capabilities. KEEP. They are intentionally composable and should not be swallowed by longer community prompts.

## Canonical technical families

### Code Review
Winner should be a rewritten canonical combining the strongest reusable criteria from GIDs 453, 1618, 337, 2259, 917, 1388 and PDF GID 2442. One visible Code Review card, with optional facets/modes: General, Security, Performance, Maintainability, Correctness, PR Review. GID 665 Pull Request Review becomes PR mode/variant. Language-specific review prompts become variants only when they contain language-specific checks that materially matter.

### Debug / Root Cause
Core /debug remains the fast command. Community Bug Discovery GID 894 and specialized debugger prompts such as GID 1267 become deeper variants/modes, not competing cards. Preserve framework-specific diagnostic knowledge only where it changes the procedure. Cross-reference AI & Prompting Root Cause Analysis family from Pass 03.

### Fix
Core /fix stays distinct from /debug because diagnosis and repair are different intents. Security-fixes GID 1431 is a Security Repair variant, not a standalone general capability.

### Refactor / Code Cleanup
Core /refactor is canonical quick command. PDF GIDs 2445 and 2459 become richer modes: performance-aware refactor and idiomatic cleanup. Do not create separate cards for wording-only differences.

### Optimize / Performance
Core /optimize remains quick generic optimization. GID 2274 Code optimisation, GID 531 large-data optimization, GID 1401 Python performance enhancer and PDF GID 2450 Performance Engineer belong to one Performance/Optimization family. Keep specialized variants only where the diagnostic method or runtime domain is materially different. Cross-reference AI & Prompting Performance Optimization family from Pass 03.

### Testing & QA
Core /tests remains fast test generation. PDF GID 2448 and Python GID 1475 become variants. App Feature Readiness Audit GID 1853 is KEEP/REWRITE as Release/Feature Readiness because it evaluates more than tests. Testing/QA family modes: Test Plan, Generate Tests, Edge Cases, Regression, Failure Paths, Coverage, Release Readiness. Cross-reference Pass 03 QA family.

### Edge Cases
Core /edgecases stays visible because it is a broadly useful thinking command beyond coding. It may link to Testing but must not be hidden inside it.

### Security & Privacy
Core /security remains fast generic review. GIDs 1466 Python Security Auditor, 1562 SaaS Security Audit, 1564 Repository Security & Architecture Audit, 1427 code-scanning/dependency analysis become modes/variants under Security Audit when reusable. Preserve genuinely different scopes: Code/App Security, Dependency/Scanning, Architecture/Threat Boundaries, SaaS/Multi-Tenant. PDF personal cybersecurity/privacy prompts GIDs 2860, 2865, 2885 belong under Everyday Security/Privacy, not Coding.

### Architecture
GIDs 1089 and 1592 Backend Architect -> one Backend Architecture capability. GID 2055 React/Next Frontend Architect -> Frontend Architecture variant/capability if full text is reusable. GID 313 Architect Guide is primarily learning/mentoring and should MOVE to Learning if retained. Cross-reference System Architect/API Design/Database Architect/Infrastructure Architect from Pass 03. Avoid generic 'senior engineer' cards when architecture intent is already covered.

Architecture should expose facets rather than dozens of cards: System, Backend, Frontend, API, Database, Infrastructure, Integration, State Management, Migration, Scalability.

PDF GIDs 2460 Infrastructure Architect, 2468 State Management Advisor, 2881 Integration Architect, 2456 Migration Planner are KEEP as distinct architecture intents/modes. GID 2875 consumer tool migration moves to Everyday Tech.

### Technical Debt
PDF GID 2472 Technical Debt Assessor -> KEEP/REWRITE. Distinct prioritization capability, not merely code review.

### Accessibility
PDF GID 2464 Accessibility Auditor -> canonical candidate and cross-reference Accessibility family from earlier passes. One accessibility audit capability; variants for UI/code/document only if materially different.

### Documentation
PDF GID 2457 Docs Writer -> KEEP/REWRITE as Code Documentation / README Generator. Cross-reference documentation automation/design handoff prompts; do not merge documentation generation with documentation synchronization if workflows differ.

### CI / DevOps / Build
PDF GID 2453 CI Pipeline -> KEEP as CI/CD Design. PDF GID 2467 Build Tool Debugger -> KEEP as Build Troubleshooting. Platform-specific statusline/project setup prompts are generally REMOVE or narrow variants unless broadly reusable.

### Code Conversion / Language Transformation
GID 303 Any Language to Python -> KEEP as Convert Code to Python or generalize to Code Translator if other languages exist. PDF GID 2462 JavaScript-to-TypeScript -> TypeScript Migration variant. Preserve semantic equivalence/testing requirements in canonical rewrite.

### Explain Technology / Technical Learning
PDF GID 2857 Explain Technology, GID 2879 Emerging-Tech Educator and GID 2872 Coding Tool Guide should MOVE to Learning/Technology rather than remain Engineering cards. They are useful capabilities.

### Network Troubleshooting
PDF GID 2873 -> KEEP/REWRITE as Network Troubleshooter. Cross-reference Network Engineer family from Specialist Roles. Prefer diagnosis by layer/device/router/provider over generic network persona.

### Regex
PDF GID 2452 -> KEEP. Strong compact specialized utility with explanation + positive/negative tests.

### No-code / AI workflow / Tool selection
PDF GIDs 2863 No-Code Builder, 2861 AI Tools Strategist, 2883 AI Workflow Designer -> KEEP but MOVE to AI & Productivity/Planning. These are end-user capabilities, not software engineering duplicates.

## REMOVE / salvage methodology only

One-off build briefs should not occupy permanent PromptDeck cards when a general builder capability can produce them: 2046 game, 3D Space Explorer, Auto File Renaming portal, sales funnel app, banking CRUD app, budget tracker, DDQN Snake, self-hosted dashboard, Clash of Clans tool, Czech invoice app, Pomodoro, Quizflix, recipe finder, calculator, portfolio site, named simulation centers, Streaks, and similar project-specific requests. Salvage unusually good requirements/checklists into a general App Builder canonical only if they add reusable value.

Vendor/project-specific prompts such as Claude Code statusline and contaminated local-project entries -> REMOVE from shipping catalog unless generalized.

Interpreter/terminal roleplay GIDs 221 Python Interpreter, 241 R Interpreter, 186 SQL Terminal -> REMOVE or place in a small Simulation/Practice collection only if the product intentionally supports it. ChatGPT should not imply actual execution when it is only simulating output.

Generic framework personas such as 'Senior Frontend Developer', 'Next.js Specialized Developer', 'Senior Java Backend Engineer', 'Smart Application Developer Assistant' should not survive merely as roles. KEEP only when full prompt contains a reusable workflow not covered by canonical Build/Architecture/Debug families.

## PDF collection judgment

The imported PDF technical prompts are generally high-value because many encode a specific job-to-be-done plus useful expected output. Do not discard them merely because they are short. Examples worth preserving include migration planning, performance diagnosis, regex with tests, technical-debt prioritization, state-management advice, infrastructure scaling, accessibility audit, network troubleshooting, CI design and documentation. Their role-opening phrase ('Act as...') can usually be removed in canonical rewrites without losing capability.

Game-design PDF prompts in packet 03 (lore, mechanic, narrative, quest, puzzle, roguelike, boss, NPC, tutorial, monetization) are not technical duplicates; MOVE them to Creative/Game Design and review there as a coherent family.

## Resulting navigation principle

Do not make the user browse by programming persona. Browse by intent first:

Build | Review | Debug | Fix | Refactor | Optimize | Test | Secure | Architect | Migrate | Document | Explain

Then facets narrow language/framework/system area. This collapses many near-duplicate 'expert roles' while preserving useful specialist knowledge.

## Cross-reference rule

A short core command and a deep canonical card may coexist when they serve different interaction depth. Example: /debug = immediate composable command; Debug & Root Cause = guided deep workflow. Two long cards that differ only by persona wording should not coexist.