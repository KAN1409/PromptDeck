# Human Curation V6 — Rescue Pass 01

This pass manually corrects false-negative patterns observed in V5. It is an editorial review artifact, not a production mutation.

## Rescue to REWRITE_CANONICAL

The following V5 removals represent durable ChatGPT capabilities. Their current source wording may still be weak, so the capability is rescued without automatically preserving the old text.

- GID 196 — `/Fallacy Finder` → **REWRITE_CANONICAL** — distinct argument-quality capability: identify fallacies, quote/locate the problematic reasoning, explain why it fails, and suggest a stronger formulation.
- GID 286 — `/Prompt Enhancer` → **REWRITE_CANONICAL** — distinct meta-prompting capability: improve a supplied prompt while preserving intent and making task/context/constraints/output explicit.
- GID 284 — `/Note-Taking assistant` → **REWRITE_CANONICAL** — reusable note-processing capability: structure raw notes, preserve facts, extract decisions/actions/open questions, and avoid inventing missing content.
- GID 172 — `/Financial Analyst` → **REWRITE_CANONICAL** — reusable analytical capability; should be reframed around evidence, assumptions, calculations, uncertainty, and decision-relevant output rather than persona alone.
- GID 153 — `/Recruiter` → **REWRITE_CANONICAL** — reusable hiring workflow capability: evaluate candidate/job fit against explicit criteria and separate evidence from inference.
- GID 190 — `/Tech Reviewer` → **REWRITE_CANONICAL** — reusable product/technology evaluation capability using consistent criteria, trade-offs, evidence, and recommendation.
- GID 152 — `/Cyber Security Specialist` → **REWRITE_CANONICAL** — reusable defensive security analysis capability; scope and safety constraints belong in the canonical version.
- GID 151 — `/UX/UI Developer` → **REWRITE_CANONICAL** — useful UX/UI critique and implementation-guidance capability; should focus on usability, hierarchy, accessibility, consistency, and actionable fixes.
- GID 183 — `/Statistician` → **REWRITE_CANONICAL** — reusable statistical reasoning capability: choose/justify methods, state assumptions, quantify uncertainty, and distinguish descriptive from inferential claims.
- GID 214 — `/Journalist` → **REWRITE_CANONICAL** — reusable reporting/interview capability when reframed around sourcing, verification, questions, structure, and uncertainty.
- GID 216 — `/Public Speaking Coach` → **REWRITE_CANONICAL** — reusable critique/rehearsal capability covering clarity, structure, delivery, audience fit, and concrete revisions.
- GID 229 — `/Machine Learning Engineer` → **REWRITE_CANONICAL** — reusable ML engineering capability covering problem framing, data, evaluation, implementation trade-offs, and failure modes.
- GID 247 — `/Software Quality Assurance Tester` → **REWRITE_CANONICAL** — reusable test-design capability covering risk, cases, edge conditions, expected behavior, reproducibility, and regression.
- GID 227 — `/Legal Advisor` → **REWRITE_CANONICAL** — useful legal-information/document-analysis capability, but canonical wording must avoid unsupported certainty and distinguish information/issue spotting from jurisdiction-specific professional advice.
- GID 170 — `/Automobile Mechanic` → **REWRITE_CANONICAL** — useful diagnostic capability if reframed as symptom → likely causes → checks → evidence → repair priority, without pretending to physically inspect the vehicle.

## Keep removal candidates removed

Examples from the V5 sample that remain appropriate removals unless a later packet reveals a materially different reusable workflow:

- `/Character`, `/Stand-up Comedian`, `/Rapper`, `/Magician`, `/Pirate`, `/Drunk Person`, `/Spongebob's Magic Conch Shell` — novelty/persona surface rather than durable workflow capability.
- `/Unconstrained AI model DAN` — jailbreak/persona artifact, not a useful canonical workflow.
- `/Midjourney Prompt Generator` — model-specific wrapper; any reusable visual-prompt capability should live in the image-generation family instead.
- `/Wikipedia Page` — output imitation alone is weaker than a canonical encyclopedia-style explainer/research workflow and should not survive merely as a branded format.

## Next review order

1. Finish rescue review of V5 removals category-by-category.
2. Compare rescued capabilities against existing KEEP items to select one canonical representative per intent.
3. Review V5 VARIANT items for false consolidation: promote a variant when it materially changes workflow, evidence standard, or output.
4. Write canonical ChatGPT-first replacements only after the capability map is stable.
5. Produce a final proposed catalog diff for explicit approval before touching shipping assets.
