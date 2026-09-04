# V7 Fast Track — Batch 03

Human editorial decisions for the remaining families visible in the global V3 family analysis. Similarity is used only to surface candidates; user outcome determines consolidation.

## Consolidate / canonicalize

### Functional Analysis
`Functional Analyst` + `Small Functional Analyst mode` -> one **Functional Analysis** capability. The small mode becomes `Quick` variant; canonical should identify actors, requirements, rules, inputs/outputs, edge cases, dependencies, acceptance criteria, and unresolved questions without inventing business rules.

### Sports / Upcoming Events Finder
Olympic weekly listing + generic sports weekly listing -> one **Upcoming Sports Events** capability if retained. Sport/competition/date range/location are inputs/facets, not separate cards. Move from AI & Prompting to Everyday/Research. Do not imply live schedule knowledge without web access.

### Task Planning
`Gerador de Tarefas` + `Planjedor de Tarefas` -> debrand/translate and compare with existing planning families. Consolidate into **Task Breakdown** if the useful behavior is turning a goal into sequenced tasks; otherwise merge into Plan/Project Planner. Portuguese wording is not a reason for a separate card in the English-only catalog.

### Lead Generation
Email Lead Generator & Tracker + vendor-specific WordPilot version -> retain only a general **Lead Generation Plan** capability if methodology is reusable. Remove WordPilot branding and any unsupported tracking/CRM execution claims. Do not merge with Cold Email: identifying/prioritizing leads and writing outreach are distinct outcomes.

### Frontend Development
Frontend Developer Agent Role + Frontend Developer Skill + React/Next.js frontend variants -> one **Frontend Development** family with framework facets. Keep **Frontend Architecture** as a deeper architecture mode/capability if it reasons about component boundaries, state, rendering, performance and maintainability rather than simply implementing UI.

### Safe Kids Media Analysis
ChildSong Guardian + SafeKids Video Analyzer -> one **Child Media Safety Review** family only if source prompts provide reusable age-appropriateness/content-analysis criteria. Media type (`song`, `video`) becomes facet. Avoid claiming definitive child-safety certification.

### Formatting
`formattg` + `formatgdoc` -> compare full prompts; if both only restructure supplied text/documents, consolidate into **Format Document/Text**. If they are contaminated/project-specific, remove instead. Formatting must remain distinct from Rewrite because it should preserve wording unless asked otherwise.

## Keep distinct despite similarity

### Research vs Writing placement
Investigative Research belongs Research & Analysis even if source was under Writing. Category misplacement is corrected rather than treated as a new capability.

### Translation vs Improvement
Chinese-English translation stays under Translation. Multilingual Writing Improvement stays under Rewrite/Improve. They can share language facets but not one card.

### Repository family hierarchy
- **Repository Understanding**: comprehend structure, architecture, dependencies, behavior.
- **Repository Audit**: identify defects/risks/debt and recommend remediation.
- **Codebase Recon**: rapid orientation and where-to-look-first workflow.
These can be sibling modes/cards under one Repository facet but should not be collapsed if their output/use case remains materially different.

## Image/navigation family decisions

### Rowboat / lakeside scenes
Serene Evening Rowboat, Cinematic Sunset Boat, Autumn Lakeside Illustration share mood/setting but not necessarily output. Place under `Landscape/Scene > Lakeside/Boat` discovery facet. Retain distinct visual variants; do not expose three near-identical top-level cards if the detail view can present scene presets.

### Sunset / dusk fantasy
SunsetMeadowDreamscape, AfterDuskNorthernLandscape, DuskFantasyTeenPortrait share time/mood but differ subject and composition. `Dusk/Sunset` becomes a lighting/time facet, not a canonical family that deletes prompts.

### Ornate / pastel / vibrant fashion portrait
These are distinct treatments. Group under `Portrait > Editorial/Stylized`; preserve as variants rather than one merged prompt.

### Dynamic visual family
DynamicCloseUpMovement, MacroVibrantFantasyNature, DynamicMonochromeWithRedAccent are a false semantic cluster. Split by intent/subject: movement portrait, macro fantasy nature, monochrome accent treatment.

### Ankara scene recipes
Location-only clustering is insufficient. `Ankara` becomes location/scene metadata. Generalizable visual treatment survives; overly specific narrative snapshots with low reuse are removal candidates.

### Fashion portrait generation
Detailed fashion/portrait prompt + `Womanized` + bikini prompt are not a safe or useful canonical family based on title similarity. Keep only a general **Fashion Portrait** capability if source quality warrants; gender/clothing are user inputs, not separate prompt cards.

## Remove / demote

- Random Girl -> remove unless full prompt demonstrates a reusable non-gimmick capability.
- Generic named `Sales` card -> remove/merge after full-text check; title alone is not a capability.
- Platform-specific Selar automation ideas -> remove platform-specific top-level card; salvage general Digital Product/Automation Ideation only if valuable.
- Named-framework/task-system branding without unique reusable method -> remove branding and merge method, or remove entirely.
- One-off Ankara/Turkish TV snapshot prompts -> demote to scene variants or remove if not reusable; never keep because they happened to cluster.

## Facet rules reinforced

The following usually become facets/inputs rather than top-level duplication:
- language / language pair
- programming framework
- location
- sport/competition
- media type
- subject gender/clothing
- time of day / lighting
- visual intensity

The following usually justify distinct capabilities when the outcome differs:
- understand vs audit vs fix
- generate vs analyze
- translate vs improve
- find leads vs write outreach
- format vs rewrite
- plan vs execute/build

## Next fast-track target

The global V3 report is now largely exhausted as a high-confidence family source. Next phase should generate a broader candidate-family index from all 3,384 entries by normalized capability/intent, specifically to catch *missed* duplicates that the earlier embedding thresholds never grouped. Human curation remains the decision layer.