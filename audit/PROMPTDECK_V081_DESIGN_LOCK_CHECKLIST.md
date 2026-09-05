# PromptDeck v0.8.1 — Pixel-Lock Design Checklist

Reference: approved PromptDeck v0.8.1 proposal image from product review.

## 1. Product identity
- [ ] Dark premium UI only.
- [ ] Discovery-first, capability-first, ChatGPT-first.
- [ ] Dense but clean; no oversized decorative panels.
- [ ] English-only visible UI.
- [ ] No separate built-in Prompt Library destination.
- [ ] My Prompts is reserved for custom prompts and Favorites.

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

### Geometry
- [ ] Standard cards: 16–20dp radius; target 18dp.
- [ ] Inputs: 14–18dp radius; target 16dp.
- [ ] Buttons: 14–18dp radius; target 16dp.
- [ ] Chips: 18–22dp radius; target 20dp.
- [ ] Icon tiles: 10–14dp radius; target 12dp.
- [ ] Borders: 1dp, low contrast.
- [ ] Shadows/elevation: subtle only, 0–2dp preferred.

### Spacing
- [ ] Main horizontal screen padding: 16–20dp; target 16dp.
- [ ] Major section spacing: 14–20dp.
- [ ] Card internal padding: 12–16dp.
- [ ] List row vertical padding: 10–12dp.
- [ ] Chip gap: 8dp.
- [ ] Primary button height: 48–52dp.
- [ ] Bottom navigation height: 64–72dp.

### Typography
- [ ] System modern sans family (`sans-serif` / Roboto-equivalent).
- [ ] Screen title: 24–28sp, medium/semibold.
- [ ] Section label: 14–16sp medium.
- [ ] Prompt/category title: 15–17sp medium.
- [ ] Description/body: 11–13sp regular.
- [ ] Bottom-nav labels: 9–11sp.
- [ ] Tags/chips: 10–11sp.
- [ ] Command identifiers are tertiary metadata, not the visual title.

## 3. Global bottom navigation
Exactly five persistent destinations:
- [ ] Home — house icon.
- [ ] Browse — search/explore icon.
- [ ] Stack — layered/stack icon.
- [ ] My Prompts — document icon.
- [ ] Settings — gear icon.
- [ ] Active item uses bright blue; inactive items use muted gray-blue.
- [ ] Icon above label.
- [ ] No sixth persistent destination.

## 4. Home — Discovery First
- [ ] PromptDeck brand header.
- [ ] Settings shortcut at top right.
- [ ] Heading: `Find the right prompt`.
- [ ] Supporting line: `What do you want to do?`.
- [ ] Full-width natural-language discovery field.
- [ ] Placeholder similar to `e.g. plan a trip, write a resume, explain a topic...`.
- [ ] Quick Goals appear as compact colored tiles, not full-width rows.
- [ ] Required Quick Goals: Write or rewrite; Research something; Think & decide; Plan something; Learn something; Fix a technical problem; Create or edit an image.
- [ ] First six goals in compact grid; image goal may span wider.
- [ ] Smart Collections shown below in compact two-column cards.
- [ ] Required Smart Collections: Compare & choose; Best for ChatGPT; Career toolkit; Content studio.
- [ ] No category-only Home.

## 5. Browse Categories
- [ ] Title: `Browse Categories`.
- [ ] Search field immediately below title.
- [ ] Vertical category cards with colored icon tile, title, one-line description, unique canonical count, chevron.
- [ ] Row height visually compact (about 62–76dp).
- [ ] Category count owns each canonical prompt exactly once.
- [ ] Visible category naming stays close to the approved structure where taxonomy allows: Writing & Content; Research & Learning; Productivity & Planning; Career & Business; Technology & Development; Creativity & Design; Health & Lifestyle; Science & Education; Images & Visuals.

## 6. Category / Subcategory
- [ ] Back affordance.
- [ ] Colored category icon + title + descriptor + count.
- [ ] Horizontal subcategory chips; first chip `All`.
- [ ] Active chip strongly highlighted; inactive chips dark/outlined.
- [ ] Prompt rows are compact cards.
- [ ] Each prompt row: colored icon tile, capability-first title, one-line description, favorite star, overflow/menu affordance.
- [ ] Internal `/command` is secondary/tertiary only.

## 7. Prompt Detail
- [ ] Back affordance, favorite, overflow.
- [ ] Colored prompt icon tile.
- [ ] Capability-first title + subtitle.
- [ ] Small semantic tags where useful.
- [ ] Main ChatGPT-native instruction in a dedicated rounded card.
- [ ] No Claude/Gemini/Cursor runtime assumptions unless the external model is explicitly the intended output target.
- [ ] No forced private chain-of-thought exposure.
- [ ] `Variables (optional)` section appears when template variables exist.
- [ ] Variables are editable fields, not raw syntax.
- [ ] Primary `Add to Stack` CTA uses locked blue→purple gradient.
- [ ] `Try it now` multiline context field.
- [ ] `Run with ChatGPT` gradient CTA.
- [ ] Related Prompts section at the bottom.

## 8. Prompt Stack
- [ ] Header `Prompt Stack` + count badge + Clear action.
- [ ] Compact ordered step cards.
- [ ] Each step shows number, icon tile, capability title, one-line description, overflow/options.
- [ ] Reordering and removal supported.
- [ ] `Add Another Prompt` secondary action.
- [ ] `Run Stack with ChatGPT` full-width gradient CTA.
- [ ] Stack composition treats the user context as source of truth.
- [ ] Earlier modules cannot override/block later modules.
- [ ] Template values are resolved before sending.
- [ ] Missing essential information triggers at most one concise clarifying question; otherwise use reasonable assumptions.
- [ ] Final output is one coherent answer; no pasted multi-answer fragments.

## 9. My Prompts
- [ ] Header `My Prompts`.
- [ ] Segmented control: `My Prompts` / `Favorites`.
- [ ] Active segment uses bright blue fill.
- [ ] Custom prompt cards use the same compact card language.
- [ ] `Create a New Prompt` secondary/outlined action.
- [ ] Import/export remain secondary utilities.
- [ ] Built-in catalog is not duplicated here.

## 10. Search
- [ ] Header `Search`.
- [ ] Search field directly below.
- [ ] Filter chips: All; Prompts; Categories; Collections.
- [ ] Smart/local relevance ranking, not literal title-only matching.
- [ ] Results use the same capability-first prompt row component.
- [ ] Browse remains the active bottom-nav destination while searching.

## 11. Settings
- [ ] Minimal list screen.
- [ ] App Preferences.
- [ ] ChatGPT Connection.
- [ ] Data & Storage.
- [ ] About PromptDeck — version visible.
- [ ] Each setting row: small rounded-square icon, title, subtitle, chevron.
- [ ] No dashboard widgets or clutter.

## 12. Component rules
- [ ] Primary CTA always uses the same blue→purple gradient family.
- [ ] Secondary actions use dark surface + subtle outline.
- [ ] Inputs are dark, bordered, rounded and compact.
- [ ] Chips are small pills; selected state is unambiguous.
- [ ] Category color is used for orientation, not decoration.
- [ ] No rainbow overload.
- [ ] No thick borders or harsh shadows.

## 13. ChatGPT-first behavior
- [ ] Every built-in prompt is directly usable with ChatGPT.
- [ ] PromptDeck is a prompt discovery/customization/stacking tool, not a chatbot.
- [ ] Raw `${...}` and genuine `[placeholder]` variables are resolved before sending.
- [ ] JSON/array brackets are never misclassified as variables.
- [ ] Tool/model instructions are conditional on actual availability.
- [ ] No request to expose private chain-of-thought.
- [ ] Short prompts remain short when that is optimal.
- [ ] Long imported/agent dumps are compacted when their capability can be preserved with less noise.

## 14. Hard no-drift failures
The release FAILS if any of these occur:
- [ ] Home becomes category-only.
- [ ] Built-in `Prompt Library` destination returns.
- [ ] `/command` names become the primary visible title.
- [ ] Quick Goals disappear.
- [ ] Smart Collections disappear.
- [ ] Natural-language discovery disappears.
- [ ] Bottom nav has anything other than five destinations.
- [ ] Primary CTA gradient changes materially.
- [ ] UI becomes light/white or Material-You oversized.
- [ ] Raw variables reach the final ChatGPT prompt.
- [ ] One canonical prompt is counted in multiple primary categories.
- [ ] Settings becomes visually complex.
- [ ] Screen structure drifts by more than ~15% without explicit approval.

## 15. Release visual gate
Before an APK is called final:
- [ ] Home matches the approved discovery-first composition.
- [ ] Browse uses compact icon/title/description/count category rows.
- [ ] Category screen uses horizontal subcategory chips + compact prompt rows.
- [ ] Prompt Detail includes instruction, variables where applicable, Add to Stack, Try it now, Run with ChatGPT, Related Prompts.
- [ ] Prompt Stack matches the compact multi-step workflow visual language.
- [ ] My Prompts contains custom prompts + Favorites only.
- [ ] Search has All/Prompts/Categories/Collections filtering.
- [ ] Settings is minimal.
- [ ] Bottom navigation is consistent on every main screen.
- [ ] Locked palette, radii, typography and density are respected.
- [ ] No visible Arabic UI.
- [ ] Canonical prompt count equals the unique built-in prompt count.
- [ ] Screenshot review shows no unexplained structural drift from the approved v0.8.1 proposal.

**Design principle:** Discovery first. Capability first. ChatGPT first. Dark, compact, controlled and premium.
