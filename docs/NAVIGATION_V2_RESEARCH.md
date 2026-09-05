# PromptDeck Navigation V2 — research and information architecture

Date: 2026-09-05

## Product problem

PromptDeck has ~3.4k prompts. A category-only browser forces users to know what they want before they can find it. The target experience is discovery-first: a user who does not know a prompt name should reach a strong prompt in 2–3 interactions.

## Patterns worth borrowing

### Raycast — universal command/search surface
Raycast Root Search and Search AI Commands treat commands as a searchable action library. AI Commands support tags and filtering. Useful pattern for PromptDeck: one universal entry point, fast ranking, tags/facets as a secondary layer rather than the primary hierarchy.

Source: https://manual.raycast.com/ai/ai-commands

### Linear — recent items, relevance ranking, filters, favorites/custom views
Linear search spans workspace objects, shows recent items, ranks by relevance, and supports filters. Custom views and favorites turn repeated discovery into one-click access.

Sources:
- https://linear.app/docs/search
- https://linear.app/docs/filters
- https://linear.app/docs/custom-views
- https://linear.app/docs/favorites

### Notion — one corpus, many views
Notion keeps one database while allowing multiple views, filters, sorts and groups. Useful pattern: categories are only one view over the same prompt corpus; collections and intent views can coexist without duplicating prompts.

Source: https://www.notion.com/help/views-filters-and-sorts

### Steam — recent shelf + dynamic collections
Steam Library Home exposes recent items and customizable shelves. Dynamic Collections automatically populate from tags/filters. Useful pattern: PromptDeck Smart Collections should be dynamic queries over prompt metadata and capability tags, not copied prompt lists.

Source: https://store.steampowered.com/libraryupdate?l=english

### Pinterest — guided refinement for users who do not know the final query
Pinterest search offers suggested topics and Guides that progressively narrow a broad idea. Useful pattern: PromptDeck starts with a broad goal, then offers intent refiners such as Edit image → Background / Lighting / Restore / Style.

Source: https://help.pinterest.com/en/article/search-for-ideas-on-pinterest

### Alfred — collections + keywords
Alfred snippets combine collections with keyword access. Useful pattern: keep explicit categories/collections for deterministic browsing while also providing fast keyword retrieval.

Source: https://www.alfredapp.com/help/features/snippets/collections/

### AIPRM — favorites/lists
AIPRM separates favorites, owned and hidden prompts into reusable lists. Useful pattern: user-curated shortcuts should sit beside algorithmic collections rather than inside the taxonomy.

Source: https://www.aiprm.com/tutorials/get-the-basics/how-to-create-a-list/

## Navigation model

PromptDeck should use four simultaneous access paths over one canonical prompt corpus:

1. **Universal intent search** — natural-language task query, locally ranked.
2. **Progressive goal navigation** — Goal → Refiner → ranked prompts.
3. **Smart Collections** — dynamic filtered/ranked views such as Improve a photo, Compare & choose, Research deeply, Fix code.
4. **Browse by category** — retained as a deterministic fallback, no longer the home screen.

## Home hierarchy

1. Universal search: “What do you want to do?”
2. Recent prompts
3. Quick goals
4. Smart collections
5. Browse all categories
6. My Prompts

## Progressive goal examples

- Create or edit an image → Enhance / Restore / Portrait / Background / Style / Generate
- Write or rewrite → Rewrite / Professional / Humanize / Shorten / Translate
- Research something → Deep research / Verify / Compare / Summarize / Find sources
- Think & decide → Brainstorm / Decision / Critique / Challenge / Prioritize
- Fix a technical problem → Debug / Optimize / Code review / Architecture / Tests
- Plan something → Roadmap / Checklist / Project / Trip / Risk
- Learn something → Explain / Teach / Study / Quiz / Examples

## Local ranking model

No API is required. V2 ranking uses weighted local text/capability matching:

- exact command/name match: highest weight
- title/description and subcategory match
- category match
- instruction-body match
- intent synonym expansion
- recent-use boost

Later iterations can add favorites, frequency and a compact offline semantic index without changing the IA.

## Guardrails

- One prompt belongs to one canonical category for counting.
- Smart Collections never duplicate records; they are views.
- A prompt may appear in multiple Smart Collections without affecting canonical totals.
- Category counts must sum to the canonical library total.
- Search and Smart Collections must always open the same canonical prompt detail card.
- The app remains English-only and local-first.
