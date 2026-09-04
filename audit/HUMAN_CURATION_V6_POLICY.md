# PromptDeck Human Curation V6 — Capability-First Editorial Policy

Status: audit only. No deletion from production assets and no merge to main.

## Purpose

V6 corrects the main weakness of V5: a weak or old prompt must not cause a useful capability to disappear. Review the capability first, then decide what to do with the current wording.

## Decision model

Every source item receives two independent judgments:

1. **Capability value** — Is this a reusable thing a ChatGPT user would deliberately want to do?
2. **Prompt quality** — Is this particular wording already the best concise ChatGPT-first implementation of that capability?

Allowed editorial outcomes:

- **KEEP** — useful distinct capability and current wording is already strong enough.
- **REWRITE_CANONICAL** — capability is valuable, but current wording is obsolete, generic-role boilerplate, overlong, underspecified, model-specific, or otherwise inferior. Preserve the capability and replace the wording later with a ChatGPT-first canonical prompt.
- **VARIANT** — useful meaningful specialization of a broader canonical capability. Do not consume a top-level card unless the specialization materially changes the workflow or output.
- **REMOVE** — no durable reusable capability, exact duplicate, irredeemably one-off/named-project content, incomplete extraction, novelty-only persona, or capability already fully represented by a superior canonical item with no meaningful variant value.

## ChatGPT-first canonical prompt standard

Prefer direct natural-language instructions over ceremonial roleplay. A canonical prompt should contain only what improves execution:

- the concrete task or goal;
- necessary context/input placeholders;
- meaningful constraints or evaluation criteria;
- the desired output shape when it matters;
- an explicit instruction to identify missing/uncertain information when needed.

Do not reward length. Do not require `Act as ...`. Do not retain external-agent metadata, tool manifests, MCP configuration, model-specific wrappers, or fake autonomy claims unless the capability itself requires an interaction protocol.

## Capability rescue rule

V5 `REMOVE` is never automatically final when the title/prompt expresses a useful reusable capability. In particular, generic professional roles and utilities must be reconsidered as capabilities. Examples include:

- Fallacy Finder / argument analysis
- Prompt Enhancer / prompt improvement
- Note-Taking Assistant / structured note transformation
- Financial Analyst / financial analysis
- Recruiter / candidate evaluation and recruiting workflows
- Tech Reviewer / technical product evaluation
- Cyber Security Specialist / defensive security analysis
- UX/UI Developer or design reviewer / UX critique and implementation guidance
- Statistician / statistical analysis
- Journalist / reporting and interview preparation
- Public Speaking Coach / speech critique and rehearsal
- Machine Learning Engineer / ML implementation guidance
- Software QA Tester / test design and defect analysis

These examples are not an allowlist; they demonstrate the principle.

## Family consolidation rule

Group by user intent/capability, not by superficial title similarity. Examples:

- Rewrite / proofread / simplify / professionalize can share a writing-transformation family while preserving materially different modes.
- Research / fact-check / literature review / deep research are related but not automatically duplicates; preserve different evidence workflows.
- Code review / debugging / root-cause analysis / refactoring are separate when the requested reasoning/output differs.
- Image prompts should be consolidated into visual families with meaningful style/use-case variants rather than hundreds of unrelated top-level cards.

## Removal bar

Remove only when at least one of these is true:

1. exact/near-exact duplicate with no useful specialization;
2. one-off named person/company/project request that cannot be generalized without inventing a new prompt;
3. incomplete or corrupted extraction;
4. external model/platform wrapper whose underlying capability is already represented elsewhere and adds no reusable behavior;
5. novelty/persona-only interaction with little durable utility;
6. content is not actually an instruction/template a PromptDeck user could reuse.

## Audit safety

V6 produces review artifacts only. It must not modify the shipping prompt JSON, build catalog, main branch, or release APK. Production changes require a later explicit approved application pass.
