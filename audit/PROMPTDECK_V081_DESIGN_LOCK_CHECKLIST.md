# PromptDeck v0.8.1 — Two-Page UI Lock

This file supersedes the earlier five-tab / pixel-mockup navigation specification.
The product must be understandable without learning an app hierarchy first.

## 1. Core rule
- [ ] Maximum **two main pages** in the app.
- [ ] Page 1: **Discover**.
- [ ] Page 2: **Stack**.
- [ ] No separate Home, Search, Browse, Categories, Collections, My Prompts, Favorites or Settings pages.
- [ ] My Prompts, Favorites, Settings, Import and Export are dialogs/sheets/overlays.
- [ ] Prompt Detail is an overlay/dialog, not a navigation page.
- [ ] The user should be able to reach any prompt and run it without traversing a hierarchy of screens.

## 2. Main navigation
- [ ] Bottom navigation has exactly **2 destinations**: Discover and Stack.
- [ ] Discover uses the search/discovery icon.
- [ ] Stack uses the layered-stack icon.
- [ ] Stack label may show the current selected count, e.g. `Stack (3)`.
- [ ] No five-tab navigation.
- [ ] No separate Browse/Search duplication.

## 3. Discover page
- [ ] PromptDeck brand mark and title at top.
- [ ] One small `More` overflow affordance at the top right.
- [ ] Primary heading: `What do you want to do?`.
- [ ] One natural-language field: `Search or describe your goal...`.
- [ ] Search and browsing are the same interaction, not separate pages.
- [ ] One compact category filter button.
- [ ] One compact Favorites filter button.
- [ ] Optional Clear filter chip appears only when needed.
- [ ] Quick intents are compact horizontal chips only: Write, Research, Plan, Learn, Code, Images.
- [ ] No large Quick Goal dashboard tiles.
- [ ] No Smart Collection dashboard section.
- [ ] No category dashboard.
- [ ] Default state shows a short Recommended list.
- [ ] Query state shows Best matches.
- [ ] Category selection happens in a picker dialog.
- [ ] Result rows show only: icon, capability-first title, one-line description, add/check affordance.
- [ ] No star + overflow + add trio on every result row.
- [ ] Tapping the row opens Prompt Detail overlay.
- [ ] Tapping `+` adds directly to Stack.

## 4. Prompt Detail overlay
- [ ] Opens as a dialog/sheet over Discover, not a new page.
- [ ] Shows capability-first title and short description.
- [ ] Shows a compact prompt preview; extremely long instructions are truncated for readability.
- [ ] Template variables appear as fields when present.
- [ ] Actions: Add to Stack, Run now, Favorite, Close.
- [ ] No back-navigation hierarchy is created.

## 5. Category browsing
- [ ] Categories remain the canonical organization layer for the 3,375 prompts.
- [ ] Categories are selected from one dialog/picker, not a page.
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
- [ ] Each built-in prompt belongs to exactly one primary category.
- [ ] Category counts are shown only where useful, not as a dashboard requirement.

## 6. Stack page
- [ ] Page title: `Stack`.
- [ ] Small selected-count badge in the header.
- [ ] Clear action appears only when Stack is non-empty.
- [ ] Empty state: one sentence + `Discover prompts` CTA.
- [ ] No fake starter stack.
- [ ] Each populated row: step number, icon, capability title, one-line description, one overflow button.
- [ ] Reorder and Remove live inside the row overflow menu.
- [ ] No giant up/down/remove buttons inside the row.
- [ ] One `Your request` context field below selected prompts.
- [ ] `Add another prompt` returns to Discover.
- [ ] Primary CTA: `Run with ChatGPT`.
- [ ] Template resolution and stack-safe composition remain unchanged.

## 7. My Prompts and Favorites
- [ ] Accessible from More menu as overlays.
- [ ] My Prompts contains real custom prompts only.
- [ ] Favorites contains real favorites only.
- [ ] No fake preview content to imitate a mockup.
- [ ] Creating a custom prompt may open an editor dialog.
- [ ] Built-in prompts are never duplicated into My Prompts.

## 8. Settings and data utilities
- [ ] Accessible from More menu as an overlay.
- [ ] Settings contains App Preferences, ChatGPT Connection, Data & Storage and About.
- [ ] Import, Export and bulk Paste live under Data & Storage.
- [ ] Settings do not consume a persistent navigation destination.

## 9. Visual system
- [ ] Root background: `#07111D`.
- [ ] Surface 1: `#0D1A2A`.
- [ ] Surface 2: `#122235`.
- [ ] Input: `#132338`.
- [ ] Border: `#24364C`.
- [ ] Primary text: `#F3F7FD`.
- [ ] Secondary text: `#A6B5C8`.
- [ ] Tertiary text: `#7E90A7`.
- [ ] Primary blue: `#2C7BFF`.
- [ ] Primary purple: `#6B5DFF`.
- [ ] CTA gradient remains blue → purple.
- [ ] Standard radius approximately 14dp.
- [ ] Main horizontal padding approximately 14dp.
- [ ] Bottom navigation height approximately 58dp.
- [ ] Dense, dark, compact, premium.
- [ ] No oversized Material-You cards.

## 10. Content quality
- [ ] Capability-first titles only.
- [ ] Raw imported names are cleaned before display.
- [ ] Descriptions do not expose imported metadata wrappers such as `# TITLE`, `Act as`, or workflow scaffolding.
- [ ] Search ranking prioritizes the actual user intent, not generic keyword expansion.
- [ ] Every built-in prompt remains ChatGPT-ready.
- [ ] No raw `${...}` or genuine placeholder variables reach ChatGPT unresolved.
- [ ] No private chain-of-thought request.

## 11. Hard failures
The build fails product review if any of the following returns:
- [ ] More than two main pages.
- [ ] Five-item bottom navigation.
- [ ] Separate Search and Browse pages.
- [ ] Separate Categories or Smart Collections pages.
- [ ] My Prompts or Settings as persistent tabs.
- [ ] Fake custom prompts or fake stack contents.
- [ ] Large dashboard grids on Discover.
- [ ] More than one primary search field.
- [ ] Result rows with unnecessary competing controls.
- [ ] Layout-breaking Stack controls.
- [ ] Raw imported prompt names/descriptions dominating the UI.

**Product principle:** Search first. Choose. Stack. Run. Everything else stays out of the way.
