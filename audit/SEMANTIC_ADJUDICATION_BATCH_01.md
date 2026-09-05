# PromptDeck Semantic Adjudication — Batch 01

Basis: full exported app catalog (3,409 prompts), with full instruction text reviewed for the high-confidence non-photo similarity candidates.

This is editorial adjudication, not threshold-based deletion.

## Decisions

| IDs | Current cards | Decision | Canonical direction | Why |
|---|---|---|---|---|
| 30317 / 30319 | `Sales` / `Selarideasforautomation` | REMOVE_DUPLICATE | Keep one, rename to a descriptive Selar/Nigeria digital-product idea card | Instructions are identical. |
| 30305 / 30317 / 30319 | `Digitalproductideas` / duplicate pair above | MERGE_CANONICAL | One canonical `SelarDigitalProductIdeas` card | 30305 has the same goal and nearly the same instruction; three cards add no useful capability. |
| 30450 / 31433 | `WebApplicationTestingSkill` / `WebApplicationTestingSkillImported` | REMOVE_DUPLICATE | Keep `WebApplicationTestingSkill` | Same skill content; imported suffix is duplicate metadata. |
| 30163 / 30199 | `NoteTakingassistant` / `NoteTakingAssistant2` | REMOVE_DUPLICATE | Keep one `LectureNoteTakingAssistant` | Instructions differ only by a spelling correction (`seperated` → `separated`). |
| 30507 / 31912 | mirror-selfie room scene cards | MERGE_CANONICAL | Keep a single descriptive mirror-selfie scene card | Same scene, subject, room, camera and styling; second is largely a formatting/wording rewrite. |
| 31039 / 31071 | investigative research assistant cards | MERGE_CANONICAL | Keep the stronger expanded body under `InvestigativeResearchAssistant` | Same persona and research methodology; 31071 is an expanded revision, not a distinct capability. |
| 30369 / 30370 | virtualization comparison cards | MERGE_CANONICAL | Keep one `VirtualizationSolutionsComparison` | Same role, task and evaluation criteria; one is a shorter revision of the other. |
| 30748 / 30750 | Turkish dessert-shop photo scene | MERGE_CANONICAL | Keep one scene prompt, preferably the cleaner direct image prompt | Same scene and subject; JSON wrapping does not create a distinct user outcome. |
| 30791 / 30814 | ESP32 UI-library development | MERGE_CANONICAL_WITH_VARIABLES | One `ESP32UILibraryDevelopment` card with explicit compiler/language-standard variables | Same product and architecture; current versions conflict on C++14 vs C++17, so keeping both would create ambiguous duplicates. |
| 30506 / 30970 | frontend developer skill/agent | KEEP_CHATGPT_CANONICAL | Keep/adapt 30506; retire Claude-agent-specific duplicate after preserving any uniquely useful constraints | Same frontend capability; 30970 is packaged as another-agent runtime metadata/examples rather than a better ChatGPT card. |
| 30888 / 30889 / 30890 | minimalist editorial beauty analysis variants | PARAMETERIZE | One canonical beauty-analysis prompt with `[MODEL_BACKGROUND]`, `[FACIAL_CHARACTERISTICS]`, and skin-tone variables | The capability and composition are the same; ethnicity-specific copies should be one configurable card rather than separate navigation entries. |
| 30989 / 31228 | LLM prompt generator / Claude Code prompt generator | KEEP_CHATGPT_CANONICAL | Keep the general LLM/ChatGPT-oriented generator; remove Claude-Code-specific duplicate unless a genuinely unique coding-agent workflow is separated | User target is ChatGPT; the second card mainly swaps the target runtime and hardcodes a Claude Code task. |
| 30494 / 30495 | professional email writer cards | MERGE_CANONICAL | One `ProfessionalEmailWriter` using the richer instruction body | Same role, controls and output goal. |
| 30200 / 31370 | vegan recipe nutritionist / 7-day 1700-calorie macro plan | KEEP_BOTH | Rename for clarity | Related domain, different scope: one recipe vs a multi-day macro-constrained plan. |
| 31282 / 31363 | pre-interview dossier / company intelligence report | KEEP_BOTH | Distinguish facets: `Interview Prep` vs `Company Research` | Strong overlap in research method, but user outcome and timing differ materially. |
| 31939 / 31950 | comprehensive book summarizer / deconstruct | KEEP_BOTH | Distinguish `Summary` vs `Deep Deconstruction` | Second adds cross-theme connection/deconstruction; not just a duplicate summary card. |
| 30531 / 30654 | isometric miniature city/weather scenes | KEEP_VARIANTS | Keep both only if labeled clearly: `Clean City Miniature` vs `Weather Info Overlay` | Shared visual style, but one adds prominent weather/date/temperature UI and therefore produces a visibly different result. |
| 31404 / 31405 | build best UI/UX / improve existing app UI/UX | KEEP_BOTH | Label by lifecycle stage: `Design New App` vs `Improve Existing App` | Same framework but different starting state and actionable outcome. |
| 30592 / 30593 | PowerShell disabled-AD-user mover | MERGE_CANONICAL | One `MoveDisabledADUsers` prompt with target OU as a variable | Same task, platform and script objective. |
| 31460 / 31461 | AI-engineering course video reviewer/extractor | MERGE_CANONICAL | Keep the stronger teaching/extraction version | Same course context and zero-omission mission; one is an expanded revision. |
| 30702 / 31204 | PlainTalk / make AI write naturally | MERGE_CANONICAL | Keep the newer `PlainTalkStyleGuide` revision and expose as a natural-writing facet | Same style-guide lineage and capability; current cards are versioned revisions, not separate jobs. |

## Net effect of this batch

- Definite duplicate/merge families: **14**
- Keep-both / meaningful-variant families: **6**
- One ChatGPT-target suitability replacement: **1**
- No photo-template similarity was auto-deleted; high lexical overlap in templated photo prompts remains excluded from duplicate decisions unless the actual scene/outcome is the same.

## Next batch priority

1. Review the 65 source-dump / oversized skill candidates for `KEEP_AS_ADVANCED`, `ADAPT_FOR_CHATGPT`, or `REMOVE_BROKEN`.
2. Review the 74 Claude, 45 Gemini, 18 Copilot, 13 Cursor and other runtime-specific references for ChatGPT suitability.
3. Normalize the 120 legacy-category records into the 15 current browse categories.
4. Continue semantic adjudication below the high-confidence similarity band, grouped by capability rather than old category.