# PromptDeck v0.8.1 — Pixel-Lock Design Checklist

Reference: approved PromptDeck v0.8.1 proposal image from product review. The proposal image is the visual source of truth; broad style similarity is not sufficient.

## 1. Product identity
- [ ] Dark premium UI only.
- [ ] Discovery-first, capability-first, ChatGPT-first.
- [ ] Dense but clean; no oversized decorative panels.
- [ ] English-only visible UI.
- [ ] No separate built-in Prompt Library destination.
- [ ] My Prompts is reserved for custom prompts and Favorites.
- [ ] PromptDeck uses the three-layer blue/purple stack mark shown in the proposal, not a diamond/text substitute.

## 2. Locked design tokens
### Colors
- [ ] Root background: `#07111D`.
- [ ] Board/deep background family: `#030B14`–`#081321`.
- [ ] Surface 1: `#0D1A2A`.
- [ ] Surface 2: `#122235`.
- [ ] Input surface: `#132338`.
- [ ] Border: `#24364C`.
- [ ] Divider: `#1D2C40`.
- [ ] Primary text: `#F3F7FD`.
- [ ] Secondary text: `#A6B5C8`.
- [ ] Tertiary text: `#7E90A7`.
- [ ] Primary blue: `#2C7BFF` / `#3D82FF` family.
- [ ] Primary purple: `#6B5DFF`.
- [ ] CTA gradient: left `#2C7BFF` → right `#6B5DFF`.
- [ ] Success: `#4FD58B`.
- [ ] Favorite: `#FFCC4D`.
- [ ] Supporting accents limited to green `#2DCB8C`, gold `#E2B84E`, purple `#A85BFF`, pink `#F35C99`, red-pink `#F35B6B`, teal `#20C7C9`, lime `#58D86D`, orange `#F49A3A`, mint `#4ADFD1`.

### Geometry — proposal density lock
- [ ] Standard card radius: 14dp.
- [ ] Input radius: 14dp.
- [ ] Primary/secondary button radius: 14dp.
- [ ] Chip radius: 18dp.
- [ ] Icon-tile radius: approximately 12dp.
- [ ] Borders: 1dp, low contrast.
- [ ] Shadows/elevation: effectively flat; no visible heavy shadow.

### Spacing — proposal density lock
- [ ] Main horizontal screen padding: 14dp.
- [ ] Main top content padding: 8dp plus actual system inset when present.
- [ ] Major section spacing: approximately 12dp.
- [ ] Compact card internal padding: approximately 8–10dp.
- [ ] Standard card internal padding: approximately 10–12dp.
- [ ] Compact list-row vertical padding: approximately 7–8dp.
- [ ] Horizontal tile/chip gap: 6dp.
- [ ] Primary button height: 44dp.
- [ ] Bottom navigation height: 62dp.

### Typography — proposal density lock
- [ ] System modern sans family (`sans-serif` / Roboto-equivalent).
- [ ] Main screen title: 22sp semibold.
- [ ] Home brand: 17sp semibold.
- [ ] Section label: 13sp medium.
- [ ] Compact prompt/category title: 13sp medium.
- [ ] Detail hero title: 18sp medium.
- [ ] Description/body: 9–12sp depending hierarchy.
- [ ] Bottom-nav labels: 9sp.
- [ ] Tags/chips: approximately 9–10sp.
- [ ] Command identifiers are tertiary metadata, never the visual title.

## 3. Header structure — exact proposal behavior
- [ ] Home alone shows the PromptDeck brand row: three-layer stack mark + `PromptDeck` + Settings shortcut.
- [ ] Browse Categories does NOT repeat the PromptDeck brand row.
- [ ] Prompt Stack does NOT repeat the PromptDeck brand row.
- [ ] My Prompts does NOT repeat the PromptDeck brand row.
- [ ] Search does NOT repeat the PromptDeck brand row.
- [ ] Settings does NOT repeat the PromptDeck brand row.
- [ ] Category/Subcategory and Prompt Detail use a compact back affordance rather than the global brand row.
- [ ] Top-level Browse, Stack, My Prompts, Search and Settings begin directly with their screen title.
- [ ] No extra explanatory subtitle is inserted under Browse Categories, Prompt Stack, My Prompts, Search or Settings unless explicitly approved later.

## 4. Global bottom navigation
Exactly five persistent destinations:
- [ ] Home — real house vector icon.
- [ ] Browse — real search vector icon.
- [ ] Stack — real layered-stack vector icon.
- [ ] My Prompts — real document vector icon.
- [ ] Settings — real gear vector icon.
- [ ] Do not substitute Unicode glyphs such as `⌂`, `⌕`, `≋`, `▣`, `⚙` for the navigation artwork.
- [ ] Active item uses bright blue; inactive items use muted gray-blue.
- [ ] Icon above label.
- [ ] No sixth persistent destination.

## 5. Home — Discovery First
- [ ] PromptDeck brand header appears only here.
- [ ] Settings shortcut at top right is compact and icon-only.
- [ ] Heading: `Find the right prompt`.
- [ ] Supporting line: `What do you want to do?`.
- [ ] Full-width natural-language discovery field.
- [ ] Placeholder similar to `e.g. plan a trip, write a resume, explain a topic...`.
- [ ] Quick Goals appear as compact colored tiles, not full-width rows.
- [ ] Required Quick Goals: Write or rewrite; Research something; Think & decide; Plan something; Learn something; Fix a technical problem; Create or edit an image.
- [ ] First six goals use a compact three-column grid.
- [ ] First six goal cards target approximately 74dp height.
- [ ] Image goal is a wider single card targeting approximately 52dp height.
- [ ] Smart Collections shown below in compact two-column cards.
- [ ] Smart Collection cards target approximately 54dp height.
- [ ] Required Smart Collections: Compare & choose; Best for ChatGPT; Career toolkit; Content studio.
- [ ] `See all` is a compact blue text action aligned to the Smart Collections heading.
- [ ] No category-only Home.

## 6. Browse Categories
- [ ] Title: `Browse Categories` and no repeated PromptDeck brand row.
- [ ] Search field immediately below title.
- [ ] Vertical category cards with colored icon tile, title, one-line description, unique canonical count, chevron.
- [ ] Category rows are visibly denser than the previous v0.8.1 RC.
- [ ] Category count owns each canonical prompt exactly once.
- [ ] Visible category naming stays close to the approved structure where taxonomy allows: Writing & Content; Research & Learning; Productivity & Planning; Career & Business; Technology & Development; Creativity & Design; Health & Lifestyle; Science & Education; Images & Visuals.

## 7. Category / Subcategory
- [ ] Compact back affordance; no global brand row.
- [ ] Colored category icon + title + descriptor + count form one hero row.
- [ ] Horizontal subcategory chips; first chip `All`.
- [ ] Active chip strongly highlighted; inactive chips dark/outlined.
- [ ] Prompt rows are compact cards.
- [ ] Each prompt row: colored icon tile, capability-first title, one-line description, favorite star, overflow/menu affordance.
- [ ] Internal `/command` is secondary/tertiary only.

## 8. Prompt Detail
- [ ] Compact back affordance; no global brand row.
- [ ] Favorite and overflow controls.
- [ ] Colored prompt icon tile.
- [ ] Capability-first title + subtitle in the hero row.
- [ ] Small semantic tags where useful.
- [ ] Main ChatGPT-native instruction in a dedicated rounded card without redundant oversized headings.
- [ ] No Claude/Gemini/Cursor runtime assumptions unless the external model is explicitly the intended output target.
- [ ] No forced private chain-of-thought exposure.
- [ ] `Variables (optional)` section appears when template variables exist.
- [ ] Variables are editable fields, not raw syntax.
- [ ] Variable fields and `Add to Stack` live in the same compact variable card when variables exist.
- [ ] Primary `Add to Stack` CTA uses locked blue→purple gradient.
- [ ] `Try it now` multiline context field.
- [ ] `Run with ChatGPT` gradient CTA.
- [ ] Related Prompts section at the bottom.

## 9. Prompt Stack
- [ ] Screen begins directly with `Prompt Stack`; no PromptDeck brand row or explanatory subtitle.
- [ ] When populated: count badge + Clear action.
- [ ] Compact ordered step cards.
- [ ] Each step shows number, icon tile, capability title, one-line description, overflow/options.
- [ ] Reordering and removal supported.
- [ ] `Add Another Prompt` secondary action.
- [ ] `Run Stack with ChatGPT` full-width gradient CTA.
- [ ] Empty state remains functional and honest; do not seed fake stack data merely to imitate the proposal screenshot.
- [ ] Stack composition treats the user context as source of truth.
- [ ] Earlier modules cannot override/block later modules.
- [ ] Template values are resolved before sending.
- [ ] Missing essential information triggers at most one concise clarifying question; otherwise use reasonable assumptions.
- [ ] Final output is one coherent answer; no pasted multi-answer fragments.

## 10. My Prompts
- [ ] Screen begins directly with `My Prompts`; no PromptDeck brand row or explanatory subtitle.
- [ ] Segmented control: `My Prompts` / `Favorites`.
- [ ] Active segment uses bright blue fill.
- [ ] Custom prompt cards use the same compact card language.
- [ ] `Create a New Prompt` secondary/outlined action.
- [ ] Import/export remain secondary utilities.
- [ ] Empty state is allowed when the user has no custom prompts; do not inject fake user prompts just to match mock data.
- [ ] Built-in catalog is not duplicated here.

## 11. Search
- [ ] Screen begins directly with `Search`; no PromptDeck brand row or explanatory subtitle.
- [ ] Search field directly below.
- [ ] Filter chips: All; Prompts; Categories; Collections.
- [ ] All four filter chips fit on one row without clipping (`Collections` must render in full).
- [ ] Smart/local relevance ranking, not literal title-only matching.
- [ ] Results use the same capability-first prompt row component.
- [ ] Empty/default state may differ from the populated proposal example because the proposal contains demonstration query/results.
- [ ] Browse remains the active bottom-nav destination while searching.

## 12. Settings
- [ ] Screen begins directly with `Settings`; no PromptDeck brand row or explanatory subtitle.
- [ ] Minimal list screen.
- [ ] App Preferences.
- [ ] ChatGPT Connection.
- [ ] Data & Storage.
- [ ] About PromptDeck — version visible.
- [ ] Each setting row: small rounded-square icon, title, one-line subtitle, chevron.
- [ ] Setting rows use the compact density from the proposal, not the taller first RC cards.
- [ ] No dashboard widgets or clutter.

## 13. Component rules
- [ ] Primary CTA always uses the same blue→purple gradient family.
- [ ] Secondary actions use dark surface + subtle outline.
- [ ] Inputs are dark, bordered, rounded and compact.
- [ ] Chips are small pills; selected state is unambiguous.
- [ ] Category color is used for orientation, not decoration.
- [ ] No rainbow overload.
- [ ] No thick borders or harsh shadows.
- [ ] Avoid generic Android/Unicode icon substitutions where the proposal specifies a recognizable icon.

## 14. ChatGPT-first behavior
- [ ] Every built-in prompt is directly usable with ChatGPT.
- [ ] PromptDeck is a prompt discovery/customization/stacking tool, not a chatbot.
- [ ] Raw `${...}` and genuine `[placeholder]` variables are resolved before sending.
- [ ] JSON/array brackets are never misclassified as variables.
- [ ] Tool/model instructions are conditional on actual availability.
- [ ] No request to expose private chain-of-thought.
- [ ] Short prompts remain short when that is optimal.
- [ ] Long imported/agent dumps are compacted when their capability can be preserved with less noise.

## 15. Hard no-drift failures
The release FAILS if any of these occur:
- [ ] Home becomes category-only.
- [ ] Built-in `Prompt Library` destination returns.
- [ ] `/command` names become the primary visible title.
- [ ] Quick Goals disappear.
- [ ] Smart Collections disappear.
- [ ] Natural-language discovery disappears.
- [ ] PromptDeck brand row appears on any top-level screen other than Home.
- [ ] Browse/Search/Stack/My Prompts/Settings regain explanatory subtitles absent from the proposal.
- [ ] Bottom nav has anything other than five destinations.
- [ ] Bottom-nav icons regress to Unicode glyphs.
- [ ] Primary CTA gradient changes materially.
- [ ] UI becomes light/white or Material-You oversized.
- [ ] Cards/tiles regress to the oversized density seen in the first v0.8.1 RC.
- [ ] Raw variables reach the final ChatGPT prompt.
- [ ] One canonical prompt is counted in multiple primary categories.
- [ ] Settings becomes visually complex.
- [ ] Screen structure drifts materially from the approved proposal without explicit approval.

## 16. Release visual gate
Before an APK is called final:
- [ ] Home matches the approved discovery-first composition.
- [ ] Home uses the three-layer PromptDeck mark.
- [ ] Non-Home top-level screens contain no repeated PromptDeck brand row.
- [ ] Browse uses compact icon/title/description/count category rows.
- [ ] Category screen uses horizontal subcategory chips + compact prompt rows.
- [ ] Prompt Detail includes instruction, variables where applicable, Add to Stack, Try it now, Run with ChatGPT, Related Prompts.
- [ ] Prompt Stack matches the compact multi-step workflow visual language.
- [ ] My Prompts contains custom prompts + Favorites only.
- [ ] Search has All/Prompts/Categories/Collections filtering with no clipping.
- [ ] Settings is minimal and compact.
- [ ] Bottom navigation is consistent on every main screen and uses vector icons.
- [ ] Locked palette, radii, typography and density are respected.
- [ ] No visible Arabic UI.
- [ ] Canonical prompt count equals the unique built-in prompt count.
- [ ] Actual-device screenshot review shows no unexplained structural drift from the approved v0.8.1 proposal.
- [ ] Mock/demo content differences are not treated as UI failures when the user's real data state is empty.

**Design principle:** Discovery first. Capability first. ChatGPT first. Dark, compact, controlled and premium.
