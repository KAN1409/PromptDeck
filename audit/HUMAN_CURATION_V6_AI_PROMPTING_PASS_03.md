# Human Curation V6 — AI & Prompting — Pass 03

Status: editorial audit only. No production asset changes and no merge to `main`.

This pass manually reviews the first AI & Prompting packet using the V6 capability-first standard: preserve useful ChatGPT capabilities, rewrite weak wrappers into ChatGPT-first canonical prompts, collapse overlapping specialist agents into families, and remove one-off/platform-specific/noise items.

## Canonical families and decisions

### Accessibility review
- GID 1602 `/Accessibility Auditor Agent Role` → **REWRITE_CANONICAL** — strong durable capability. Canonical should audit supplied UI/code against accessibility criteria, separate confirmed issues from unknowns, prioritize severity, and return actionable fixes.
- Cross-reference with Specialist Roles GID 739 `/Accessibility Expert` and GID 740 `/Accessibility Testing Superpower` → one **Accessibility Audit** canonical family; keep materially different testing/remediation modes as variants only.

### AI / agent security
- GID 488 `/AI Agent Security Evaluation Checklist` → **REWRITE_CANONICAL** — retain as a distinct security-review capability for AI systems; replace persona boilerplate with scope, threat areas, evidence requests, risk ranking, and mitigations.
- GID 741 `/Agent Organization Expert` → **VARIANT** under a broader **Task Decomposition & Multi-Agent Orchestration** family; useful method, but should not consume a standalone card if PromptDeck already has planning/decomposition coverage.
- GID 2058 `/Parallel Agents With Goal` → **VARIANT** under the same family; its distinct value is parallel decomposition, not a new capability.
- GID 574 `/Glyth_Maker` → **REMOVE** as branded adversarial-agent theater. Preserve only the underlying cross-check/adversarial review idea via existing critique/red-team capabilities.

### AI app / product building
- GID 1230 `/AI App Prototyping for Chat Interface` → **REMOVE** — hard-coded endpoint and one-off app specification; not a reusable generic capability.
- GID 1720 `/Creating PWA AI Chatbot` → **REMOVE** — too thin and one-off; generic app planning is already represented elsewhere.
- GID 1635 `/AI-First Design Handoff Generator (Dev-Ready Spec)` → **KEEP** — clearly reusable and output-specific. Preserve as a distinct design-handoff capability.
- GID 1093 `/Mobile App Builder` → **REWRITE_CANONICAL** — useful mobile implementation/planning capability; strip external-agent wrapper and examples.
- GID 1094 `/Rapid Prototyper` + GID 1624 `/Rapid Prototyper Agent Role` → **MERGE / REWRITE_CANONICAL** into one **Rapid Prototype / MVP Builder** capability.

### Customer support
- GID 477 `/AI Customer Support Specialist` → **REWRITE_CANONICAL** — keep as **Customer Support Response & Triage** capability: identify issue, ask only necessary clarifying questions, propose response, escalation criteria, and avoid unsupported promises.

### AI / ML engineering
- GID 1088 `/AI Engineer` → **REWRITE_CANONICAL** — retain as AI/ML implementation guidance; merge with V6-rescued ML engineering capability where overlap is substantial.
- Cross-reference with GID 229 `/Machine Learning Engineer` from Rescue Pass 01 → likely one **ML/AI Engineering** family with variants for model integration vs broader ML systems.

### Project-management artifacts
- GID 1760 `/AI Productivity Artifact Generator` → **REWRITE_CANONICAL** — useful but overbranded. Convert to **Project Artifact Generator** for backlog, roadmap, sprint board, task tracker, estimates, and chosen method.
- GID 1097 `/Sprint Prioritizer` → **KEEP or VARIANT** under a **Prioritization / Sprint Planning** family depending on overlap with existing core `/priority` and `/plan`; preserve only if its criteria and trade-off workflow materially improve results.

### API design and testing
- GID 1591 `/API Design Expert Agent Role` → **REWRITE_CANONICAL** — distinct, high-value API design review/specification capability.
- GID 1613 `/API Tester Agent Role` → **REWRITE_CANONICAL** — distinct API testing capability; keep separate from design because workflow/output differ.
- GID 1628 `/Tool Evaluator Agent Role` → **REWRITE_CANONICAL** only if cross-reference confirms no stronger generic comparison tool exists; otherwise fold into `/Tech Reviewer` / product-comparison family.

### App Store review
- GID 766 `/App Store Submission Agent` + GID 1697 `/Apple App Store Review Compliance Agent` → **MERGE / REWRITE_CANONICAL** into one **App Store Submission Review** capability with variants for metadata/compliance vs implementation readiness.

### Software reliability and architecture
- GID 1630 `/Bug Risk Analyst Agent Role` → **REWRITE_CANONICAL** — preserve defect-risk analysis.
- GID 1608 `/Caching Architect Agent Role` → **REWRITE_CANONICAL** — preserve only if its caching-specific reasoning is distinct from performance tuning; likely a technical-family variant rather than top-level card.
- GID 1593 `/Database Architect Agent Role` → **REWRITE_CANONICAL** — useful durable database design/optimization capability.
- GID 1594 `/Data Validator Agent Role` → **REWRITE_CANONICAL** — useful validation/integrity capability.
- GID 1620 `/Dependency Manager Agent Role` → **REWRITE_CANONICAL** — package/dependency resolution and supply-chain review are distinct enough to keep.
- GID 1597 `/DevOps Automator Agent Role` → **REWRITE_CANONICAL** — retain DevOps/IaC/CI-CD capability, but trim agent boilerplate.
- GID 1621 `/Error Handler Agent Role` → **REWRITE_CANONICAL** — preserve error-handling/logging/observability review.
- GID 1599 `/Git Workflow Expert Agent Role` → **REWRITE_CANONICAL** — retain Git workflow/conflict/history guidance.
- GID 1609 `/Optimization Auditor Agent Role` + GID 1610 `/Performance Tuning Agent Role` → **MERGE FAMILY**. Keep one canonical **Performance & Optimization Audit**; variants may separate diagnostic audit from implementation tuning.
- GID 1622 `/Post-Implementation Audit Agent Role` → **KEEP / REWRITE_CANONICAL** — distinct post-change verification/release-readiness workflow.
- GID 1623 `/Product Planner Agent Role` → **REWRITE_CANONICAL** — retain product planning/requirements/roadmap capability.
- GID 1614 `/Quality Engineering Agent Role` → **REWRITE_CANONICAL** — retain quality strategy; cross-reference against QA/test families to avoid duplication.
- GID 1626 `/Refactoring Expert Agent Role` → **REWRITE_CANONICAL** — distinct from generic code review because output is transformation strategy and safer refactor plan.
- GID 1632 `/Repository Indexer Agent Role` → **VARIANT** under **Codebase Understanding / Repository Analysis** family.
- GID 1600 `/Repository Workflow Editor Agent Role` → **VARIANT** under **AI Coding Instructions / Repository Rules** family; useful, but narrower than a general PromptDeck card.
- GID 1625 `/Root Cause Analysis Agent Role` → **REWRITE_CANONICAL** — keep as distinct causal-diagnosis workflow.
- GID 455 `/Senior System Architect Agent` + GID 1590 `/System Architect Agent Role` → **MERGE / REWRITE_CANONICAL** into one **System Architect** capability.
- GID 1627 `/Shell Script Agent Role` → **REWRITE_CANONICAL** — keep if no stronger shell automation card exists in Problem Solving & Technical.
- GID 1629 `/TypeScript Type Expert Agent Role` → **VARIANT** under language-specific coding expertise; should not be a top-level browse card unless technical facets expose language specialists.
- GID 1606 `/UI Architect Agent Role` → **REWRITE_CANONICAL** — keep as design-system/component-architecture capability, distinct from generic UX critique.
- GID 2176 `/Universal Instructions for React / Next.js Projects` → **VARIANT** under framework-specific coding guidance; not a standalone top-level capability.
- GID 446 `/Ultrathinker` → **REMOVE as standalone**; its durable value is rigorous software reasoning, already represented by architecture/review/debugging families.
- GID 1540 `/Unity Architecture Specialist` → **VARIANT** under game-development / software-architecture facets, not a standalone top-level card.

### Research and fact checking
- GID 1578 `/Deep Investigation Agent` → **VARIANT / MERGE** with deep-research family after stripping non-English/external-agent wrapper.
- GID 1631 `/Deep Research Agent Role` → **REWRITE_CANONICAL** — strong candidate for canonical **Deep Research** if it materially exceeds existing `/DeepHunt` in methodology; otherwise merge into `/DeepHunt` family.
- GID 1339 `/Fact-Checking Evaluation Assistant` → **REWRITE_CANONICAL** — preserve fact-check workflow, but remove fake multi-agent theatrics unless the step separation adds measurable value.
- GID 1851 `/Grok Research Agent` → **REMOVE** as model-branded wrapper; any useful methodology belongs in Deep Research.
- GID 1098 `/Trend Researcher` → **REWRITE_CANONICAL or VARIANT** under research/market-trend family.
- GID 1296 `/Sales Research` → **REWRITE_CANONICAL** — distinct prospect/company research use case; likely Business & Marketing rather than AI & Prompting.

### Planning / decision support
- GID 1165 `/Intent Recognition Planner Agent` → **VARIANT** under goal clarification/planning; likely overlaps with `/AskMeFirst`, `/DecisionQuestions`, and planning core.
- GID 2057 `/Plan Check Agent` → **REWRITE_CANONICAL** — preserve the valuable "stress-test the plan" behavior, but remove impossible "100% confidence" framing. Canonical should identify weak assumptions, failure modes, evidence gaps, and confidence limits.
- GID 1309 `/Second Opinion` → **MERGE** into existing `/SecondOpinion` capability from the curated 100; external Codex/Gemini wrapper adds no standalone value.

### SEO / content optimization
- GID 1604 `/SEO Auditor Agent Role` + GID 1605 `/SEO Optimization Agent Role` → **MERGE FAMILY** with two modes: **Audit** and **Improve**. Keep as Business/Marketing capability, not AI & Prompting.

### Testing and QA
- GID 1615 `/Test Analyzer Agent Role` → **REWRITE_CANONICAL** — distinct test-result interpretation capability.
- GID 1095 `/Test Automation Expert` → **REWRITE_CANONICAL** — test creation/execution/fix workflow; external-agent examples removed.
- GID 1616 `/Test Engineer Agent Role` → **REWRITE_CANONICAL** — broad test design strategy.
- GID 1937 `/Test-Driven Bug Hunting With Reproduction Agents` → **KEEP / VARIANT** under debugging because reproduce-first discipline is meaningfully distinct.
- Cross-reference with rescued GID 247 `/Software Quality Assurance Tester` and quality engineering entries: build one **Testing & QA** family with modes for Test Strategy, Test Cases, Automation, Analyze Failures, Reproduce Bug, and Release Audit instead of six standalone near-duplicates.

## Reclassify out of AI & Prompting

The following are not AI/prompting capabilities and should move to their real families rather than consume cards in this category:

- GID 1237 `/Create Icons` → Photo/Image / Graphic Design variant.
- GID 891 `/Dual Lighting Narrative Scene` → Photo/Image / Cinematic portrait variant.
- GID 1135 `/Fisheye 90s` → Photo/Image / Film & Vintage variant.
- GID 1197 `/Valorant Agent Style` → Photo/Image / Illustration/Game-art variant.
- GID 315 `/Tech-Challenged Customer` → Simulation / Customer-support training variant.
- GID 162 `/Real Estate Agent` → Lifestyle/Buying/Property assistance family if retained; not AI & Prompting.
- GID 950 `/Senior Product Engineer + Data Scientist for Turkish Car Valuation Platform` → REMOVE as one-off named build request; generic product/data-engineering capabilities already exist.

## Remove

- GID 1411 `/# ANTIGRAVITY GLOBAL RULES` → **REMOVE** — external-agent installation/configuration wrapper.
- GID 2279 `/Analyze Yacon Holdings Stock Trend` → **REMOVE** — incomplete, non-English, named-stock one-off.
- GID 1348 `/CLAUDE.md Generator for AI Coding Agents` → **VARIANT at most**, not top-level; it is targeted at Claude/Cursor/Windsurf rather than ChatGPT. Preserve only generic repository-instruction-writing capability elsewhere.
- GID 1039 `/Context7 Documentation Expert Agent` → **REMOVE** — external MCP/platform wrapper.
- GID 1803 `/Designing a Feature Testing Page for Enterprise WeChat/DingTalk` → **REMOVE** — named product one-off.
- GID 2062 `/Enhancing Efficiency with Codex Using Sub-Agents` → **REMOVE / merge methodology** into generic workflow-efficiency prompt; Codex-specific wording is not needed.
- GID 2177 `/Exuvia` → **REMOVE** — named external platform skill.
- GID 1167 `/gemini.md` → **REMOVE as standalone** — another-model instruction file; generic project-instruction capability may survive elsewhere.
- GID 1680 `/GitHub Enterprise Cloud administrator and power user` → **VARIANT** only if enterprise-GitHub administration is retained under technical specialists; not AI & Prompting.
- GID 1662 `/GitHub Stars Fetcher with Agent Browser` → **REMOVE** — external tool/browser-specific operation.
- GID 1889 `/Job search agent` → **REMOVE as current wording** — overly specific automation/geography/certification request; job-search capability is already represented in Work & Career.
- GID 1099 `/Joker: Tech Humor Master` → **REMOVE** — novelty persona.
- GID 1759 `/Meta Agent Builder for Letta Platform` → **REMOVE** — Letta-specific.
- GID 1374 `/MoltPass Client -- Cryptographic Passport for AI Agents` → **REMOVE** — platform-specific.
- GID 1316 `/Nurse` → **REMOVE current item** — incomplete scaffold. Any health-information capability must be separately curated with proper uncertainty/safety framing.
- GID 632 `/Osobní AI Agent pro Petra Sovadinu` → **REMOVE** — named-person, non-English one-off.
- GID 1738 `/pdfcount` → **REMOVE as current wrapper** unless full prompt reveals a general PDF counting/extraction workflow worth rewriting.
- GID 1017 `/Policy Agent Client Manager` → **REMOVE** — narrow client-record/payment workflow and fake storage/reminder claims.
- GID 1806 `/RPA/Agentic AI Process Developer Portfolio Design for Claude` → **REMOVE** — Claude-specific one-off portfolio request.
- GID 1426 `/Test` → **REMOVE** — user question, not reusable prompt.
- GID 1500 `/test` → **REMOVE** — incomplete scaffold.
- GID 1501 `/Update Agent Permissions` → **REMOVE** — Claude/Gemini tool-permission maintenance request, not a reusable ChatGPT prompt.

## Editorial conclusions from this packet

1. **AI & Prompting is currently overloaded with technical agent-role wrappers.** Many should move into Problem Solving & Technical or become family variants.
2. **The strongest reusable items are capabilities, not agent personas:** accessibility audit, API design/test, system architecture, QA/testing, research/fact-checking, root-cause analysis, product planning, and performance optimization.
3. **Several existing cards collapse cleanly into families** without capability loss: App Store review, Rapid Prototyping, System Architecture, SEO Audit/Optimize, Performance/Optimization, Testing/QA, Deep Research, and Multi-Agent/Task Decomposition.
4. **External-agent metadata should be stripped even when the underlying capability survives.** YAML skill headers, MCP/tool declarations, branded agent names, and fake autonomy do not improve ChatGPT execution.
5. **Current category placement is a major source of browsing noise.** Reclassification is as important as deletion.

Next: continue AI & Prompting packets 02–04, then cross-reference the surviving technical capabilities directly against `Problem Solving & Technical` to select canonical winners and remove duplicate surface cards.