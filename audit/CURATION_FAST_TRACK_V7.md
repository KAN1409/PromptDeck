# PromptDeck Curation Fast Track V7

## Goal
Cross-reference the full 3,384-card catalog much faster without delegating editorial survival decisions to similarity scores.

## Workflow
1. Normalize each prompt into capability, input, output, method, constraints, context, and style.
2. Ignore legacy category during candidate grouping so equivalent capabilities meet globally.
3. Group candidates into capability families. Clustering is retrieval assistance only.
4. Review each family side-by-side and assign:
   - CANONICAL: best reusable ChatGPT-first capability card.
   - MERGE: useful instructions are folded into the canonical card.
   - VARIANT: materially different outcome/method retained under the family, not as another top-level card.
   - DISTINCT: superficially similar but genuinely separate capability.
   - REMOVE: duplicate, one-off, contaminated, platform-specific, novelty-only, or low-value content.
5. Rewrite canonical prompts for current ChatGPT using clear task, relevant context, meaningful constraints, and explicit expected output. Remove decorative personas, fake expertise claims, vendor/model branding, unsupported autonomy, and redundant wording.
6. Run a second global overlap pass after family consolidation.
7. Build facets only from the cleaned capability catalog.

## Priority family queues
### Writing / communication
Rewrite; Professional rewrite; Natural/human writing; Tone change; Summarize; Email; Message; Proofread; Translate; Resume/CV; Cover letter; Social copy; Script; SEO writing.

### Research / reasoning
Deep research; Web/social/local finding; Fact-check; Compare; Evidence; Source verification; Second opinion; Critique; Decision; Brainstorm; Explain; Analyze; Extract; Literature review/gap.

### Technical
Code review; Debug; Fix; Refactor; Optimize; Tests/QA; Security; Architecture; API; Database; Performance; Migration; Documentation; Accessibility; DevOps; Troubleshooting.

### Image
Restore; Enhance; Identity preservation; Retouch; Skin realism; Face recovery; Lighting; Background; Blur; Color; Artifact repair; Portrait look; Cinematic/editorial; Style transfer; Product; Landscape; Reference matching.

### Planning / everyday / business
Plan; Prioritize; Travel; Buy/compare; Career; Productivity; Learning; Marketing; Business strategy; Customer research; Content planning.

## Human editorial rule
A weak source prompt does not imply a weak capability. If the capability is useful, rewrite it. A long prompt does not outrank a short prompt. Keep a separate card only when it creates a meaningfully different user outcome, method, or reusable context.

## Desired output
A final manifest mapping all 3,384 original GIDs to canonical family IDs and dispositions, plus canonical prompt text, meaningful variants, facet metadata, removals, and final visible-card count.

## Safety
Audit branch only. No merge to main and no shipping-catalog deletion without explicit user authorization.