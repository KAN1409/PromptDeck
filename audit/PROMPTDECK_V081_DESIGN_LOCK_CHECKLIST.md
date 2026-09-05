# PromptDeck v0.8.1 — Hybrid One-Screen UI/UX Lock

This supersedes the earlier five-tab and two-page navigation specs.
The app must be understandable immediately: either let PromptDeck choose, or browse manually.

## 1. Core architecture
- [ ] Exactly **one main workspace**.
- [ ] Landing presents two explicit paths:
  - [ ] **Ask PromptDeck** — intelligent prompt/workflow selection.
  - [ ] **Browse all prompts** — manual access to the complete catalog.
- [ ] Ask and Browse are modes inside the same workspace, not separate navigation destinations.
- [ ] A compact segmented switch lets the user change between Ask and Browse at any time.
- [ ] No persistent bottom navigation.
- [ ] No empty Stack page.
- [ ] No separate Search, Browse, Categories, Collections, My Prompts, Favorites or Settings pages.
- [ ] Prompt Detail and Review & Run are contextual bottom sheets/overlays.

## 2. Landing
- [ ] PromptDeck mark + wordmark at top left.
- [ ] One compact More affordance at top right.
- [ ] Heading: `How do you want to start?`.
- [ ] Supporting copy explains the choice in one sentence.
- [ ] Two premium entry cards only:
  - [ ] Ask PromptDeck — `Describe your goal and get the best prompt or workflow automatically.`
  - [ ] Browse all prompts — `Search and explore the complete 3,375-prompt library yourself.`
- [ ] No dashboard grid.
- [ ] No Smart Collections section.
- [ ] No categories dumped on the landing state.

## 3. Ask PromptDeck mode
- [ ] Heading asks what the user wants ChatGPT to help with.
- [ ] One natural-language goal field; multiline is allowed.
- [ ] Explicit CTA: `Find the best approach`.
- [ ] The app does not flood results while the user is typing; recommendation generation happens on explicit action.
- [ ] Output hierarchy:
  - [ ] `BEST APPROACH` — one strongest prompt.
  - [ ] `SUGGESTED WORKFLOW` — only when the task benefits from multiple capabilities.
  - [ ] `MORE MATCHES` — maximum three concise alternatives.
- [ ] Suggested workflow contains 2–4 distinct steps maximum.
- [ ] Workflow composition is intent-aware: e.g. research → compare → recommend for comparison/decision tasks.
- [ ] `Use this prompt` or `Use workflow` adds to the current selection without creating a new page.
- [ ] The user's goal becomes the default request/context for Review & Run.

## 4. Browse all prompts mode
- [ ] Search field: `Search prompts...`.
- [ ] Category filter opens a picker, not a page.
- [ ] Favorites filter is optional and compact.
- [ ] All 3,375 canonical prompts remain reachable.
- [ ] No-query state can show canonical order with progressive `Show more` pagination.
- [ ] Search state ranks by intent relevance.
- [ ] Category state filters the same result surface.
- [ ] Result rows contain only:
  - [ ] category/prompt icon
  - [ ] capability-first title
  - [ ] one-line outcome description
  - [ ] `+` / check affordance
- [ ] Tapping the row opens Prompt Detail sheet.
- [ ] Tapping `+` adds directly to the selection.

## 5. Selection / Stack behavior
- [ ] Stack is **not** a page or navigation destination.
- [ ] Nothing stack-related is shown while zero prompts are selected.
- [ ] After the first selection, a sticky bottom bar appears:
  - [ ] `<N> selected`
  - [ ] `Review & Run →`
- [ ] The sticky bar remains available in both Ask and Browse modes.
- [ ] Review & Run opens a bottom sheet over the current workspace.
- [ ] The sheet shows ordered selected prompts, request/context, Add prompt, and Run with ChatGPT.
- [ ] Reorder and Remove live behind each row overflow menu.
- [ ] No giant up/down/remove controls.
- [ ] Closing Review & Run returns to the exact workspace/mode the user was using.

## 6. Review & Run sheet
- [ ] Title: `Review & Run`.
- [ ] Selected count is visible.
- [ ] Prompt rows are compact and ordered.
- [ ] One request/context field.
- [ ] `Add prompt` returns to Browse mode.
- [ ] Primary CTA: `Run with ChatGPT`.
- [ ] Running sends directly to ChatGPT; no intermediate Final Prompt page.
- [ ] Template variables are resolved before sending.
- [ ] Stack modules execute in order and cannot override later modules.
- [ ] Final answer is coherent, not a pasted sequence of separate answers.

## 7. Prompt Detail sheet
- [ ] Bottom sheet, never a navigation page.
- [ ] Capability-first title + short description.
- [ ] Compact instruction preview; very long prompt bodies are truncated for UI readability.
- [ ] Template variables render as fields.
- [ ] Favorite action available.
- [ ] `Run now` and `Add to Stack` are the two primary actions.
- [ ] Close returns to the exact workspace state.

## 8. Categories and catalog
- [ ] Categories remain the canonical organization layer, not a navigation hierarchy.
- [ ] Exact primary categories remain:
  - [ ] Writing & Content
  - [ ] Research & Learning
  - [ ] Productivity & Planning
  - [ ] Career & Business
  - [ ] Technology & Development
  - [ ] Creativity & Design
  - [ ] Health & Lifestyle
  - [ ] Science & Education
  - [ ] Images & Visuals
- [ ] Every built-in prompt belongs to exactly one primary category.
- [ ] Category counts reflect unique canonical ownership only.

## 9. More menu
- [ ] More contains My Prompts, Favorites and Settings.
- [ ] These open overlays/dialogs only.
- [ ] My Prompts contains real custom prompts only.
- [ ] Favorites contains real favorites only.
- [ ] Settings contains App Preferences, ChatGPT Connection, Data & Storage and About.
- [ ] Import, Export and bulk Paste remain under Data & Storage.
- [ ] No persistent utility tabs.

## 10. Visual system
- [ ] Root background `#07111D`.
- [ ] Surface 1 `#0D1A2A`.
- [ ] Surface 2 `#122235`.
- [ ] Input `#132338`.
- [ ] Border `#24364C`.
- [ ] Primary text `#F3F7FD`.
- [ ] Secondary text `#A6B5C8`.
- [ ] Tertiary text `#7E90A7`.
- [ ] Primary blue `#2C7BFF`.
- [ ] Primary purple `#6B5DFF`.
- [ ] Primary CTA gradient blue → purple.
- [ ] Ask PromptDeck uses a restrained blue intelligence accent.
- [ ] Browse uses a restrained green/neutral discovery accent.
- [ ] Standard radius approximately 14–16dp.
- [ ] Main horizontal padding approximately 14dp.
- [ ] Bottom sheets use larger approximately 24dp top/surface radius.
- [ ] Dense, premium, calm; no Material-You bloat.

## 11. Presentation quality
- [ ] UI never derives an ugly raw imported command name as a primary title when clean metadata is available.
- [ ] Capability-first titles dominate.
- [ ] One-line descriptions state outcomes, not imported role scaffolding.
- [ ] Raw `# TITLE`, `Act as`, `You are`, agent/runtime wrappers do not dominate cards.
- [ ] Search/Ask ranking prioritizes actual user intent over generic words.
- [ ] Suggested workflow steps are distinct, not near-duplicate prompt variants.

## 12. ChatGPT-first behavior
- [ ] 3,375 canonical built-ins remain available.
- [ ] Every built-in is ChatGPT-ready.
- [ ] Raw `${...}` and genuine placeholders never reach ChatGPT unresolved.
- [ ] External tools/models are conditional on actual availability.
- [ ] No forced private chain-of-thought exposure.
- [ ] Ask PromptDeck may choose one prompt or a 2–4 step workflow depending on task complexity.

## 13. Hard failures
The build fails product review if any of these return:
- [ ] Persistent bottom navigation.
- [ ] Empty Stack page.
- [ ] Separate Search and Browse pages.
- [ ] Categories as a page hierarchy.
- [ ] Smart Collections dashboard.
- [ ] Fake starter Stack/custom prompts/search query.
- [ ] More than one main workspace.
- [ ] Intermediate Final Prompt navigation page.
- [ ] Large dashboard grids before the user chooses Ask or Browse.
- [ ] Result rows with star + overflow + add competing simultaneously.
- [ ] Layout-breaking reorder buttons.
- [ ] Raw imported names/descriptions dominating the UI.

**Product principle:**

> **Choose how you want to work: PromptDeck can think for you, or you can browse everything yourself. Selection appears only when it exists.**
