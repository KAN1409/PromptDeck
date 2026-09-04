# Human Curation V6 — Specialist Roles Editorial Pass 02

Status: audit only. No production prompt JSON changed. No merge to `main`.

This pass manually reviews the Specialist Roles packets against the V6 capability-first policy and current ChatGPT prompting guidance: preserve useful reusable capabilities, rewrite weak roleplay wrappers, move image recipes into visual families, and remove one-off/personal/novelty content.

## Promote or rewrite as durable capabilities

- GID 739 `/Accessibility Expert` → **REWRITE_CANONICAL** — durable accessibility-audit capability; merge conceptually with other WCAG/accessibility audit entries and keep one ChatGPT-first canonical implementation.
- GID 740 `/Accessibility Testing Superpower` → **VARIANT** under Accessibility Audit — overlapping workflow; preserve any distinct testing/remediation steps but do not surface a second top-level card.
- GID 1665 `/Analyze Chat History With User` → **REWRITE_CANONICAL** — useful conversation-analysis capability: themes, sentiment, unresolved issues, chronology, and evidence-backed observations.
- GID 2242 `/Artigo Resumidor` → **REMOVE as standalone** — article summarization is already covered by stronger general summarization capabilities; no durable specialization shown in this version.
- GID 2245 `/Aws transform` → **REWRITE_CANONICAL** — useful cloud-architecture evaluation capability if generalized to AWS transformation/migration analysis and stripped of vague roleplay.
- GID 1143 `/Markdown Task Implementer` → **REWRITE_CANONICAL** — useful file/task-execution workflow: identify requested checklist items, execute only those, preserve scope, and report completed/blocked items.
- GID 895 `/Manim Code` → **VARIANT** under educational visualization/code generation — useful specialization, but too narrow for its own top-level card.
- GID 236 `/Mathematician` → **REMOVE as standalone** — generic calculator persona is weaker than existing math/explain/solve capabilities; preserve only if a distinct symbolic-math workflow is later found.
- GID 2230 `/Maximum Lexical Compression` → **KEEP** — genuinely distinct rewriting transformation with a clear output objective.
- GID 345 `/Monthly Updates` → **VARIANT** under project/status updates — reusable, but the sponsor-specific framing is narrower than a canonical recurring-update prompt.
- GID 1667 `/Moral Dilemma Choices` → **VARIANT** under self-reflection/decision exploration — useful interaction pattern, but personality conclusions must be framed cautiously rather than as diagnosis.
- GID 1175 `/Network Engineer: Home Edition` → **REWRITE_CANONICAL** — useful home-network troubleshooting/design capability; remove author/version wrapper and retain diagnostics, topology, security, and verification steps.
- GID 1522 `/Operating systems` → **VARIANT** under study/tutoring — useful subject-specific learning prompt, not a top-level specialist card.
- GID 2041 `/Verbatim Chat to Organized Notes` → **KEEP / merge candidate with Note-Taking Assistant** — materially useful preservation-first note transformation. Prefer one canonical family with modes: concise notes vs near-verbatim organized notes.
- GID 1882 `/YouTube Script Engine — High Retention` → **REWRITE_CANONICAL** — durable content-writing capability; keep retention structure, hook, pacing, open loops, and CTA as explicit criteria.
- GID 2118 `/Ultra Brief One-Sentence Answers` → **VARIANT** under concise/shorten response controls — useful mode, but not worth a separate top-level card.
- GID 322 `/Yes or No answer` → **VARIANT** under constrained-answer modes — valid interaction control, but low standalone value.
- GID 1831 `/Sandbox Mode` → **REMOVE as standalone** — claims about memory/statelessness cannot be guaranteed by prompt wording alone; misleading capability surface.

## Move to Photo Editing & Image Generation families

These are reusable visual recipes but are misplaced as Specialist Roles. Keep only as visual variants, not top-level Specialist cards:

- GID 1965 `/.` — glasses edit → **VARIANT: Portrait Accessories / Identity Preservation**
- GID 1854 `/3D Cartoon Animation: Baby Bunny Adventure` → **VARIANT: 3D / Animation**
- GID 761 `/3D Character Render In High-End Disney Pixar Style` → **VARIANT: Stylized Character Render**
- GID 651 `/A Moment Shared with the Wild` → **VARIANT: Creative Selfie / Wildlife**
- GID 668 `/A three-panel monochromatic image` → **VARIANT: Comic / Monochrome Narrative**
- GID 2031 `/Advanced Image Quality Enhancement` → **VARIANT: Restore & Enhance**; compare against existing enhancement canonical and preserve only stronger constraints.
- GID 1433 `/Alp Dağlarındasın` → **VARIANT: Travel Portrait / Alpine**
- GID 868 `/Amateur Girls' Night Selfie - Casual and Imperfect` → **VARIANT: Candid Phone Photography**
- GID 892 `/Amateur Mirror Selfie with Natural Look` → **VARIANT: Candid Phone Photography**
- GID 406 `/Architectural Sketch & Markup Overlay` → **KEEP as visual variant** — distinct architectural markup treatment.
- GID 829 `/Art-W` → **VARIANT: Illustration Style**
- GID 810 `/Balcony Coffee (morning haze, plant vibe)` → **VARIANT: Lifestyle Candid**
- GID 780 `/Bathroom Flash Selfie` → **VARIANT: Candid Phone Photography**
- GID 698 `/berre` → **VARIANT: Identity-Locked Portrait**
- GID 1890 `/Black Effect on person` → **VARIANT: B&W / Background Treatment**
- GID 808 `/Bookstore Aisle (artsy, quiet luxury)` → **VARIANT: Lifestyle Candid**
- GID 792 `/Cafe Window Seat` → **VARIANT: Lifestyle Candid**
- GID 1464 `/cambio de ojos` → **VARIANT: Eye / Fantasy Edit**
- GID 1118 `/Cinematic Close-Up Portrait Generation` → **VARIANT: Cinematic Portrait**
- GID 1704 `/Lonely cry` → **VARIANT: Emotional Cinematic Portrait**, provided it remains non-exploitative and adult.
- GID 512 `/Luxury Ski Resort Selfie Scene Description` → **VARIANT: Travel/Luxury Candid**
- GID 1310 `/Minecraft image` → **VARIANT: Character Transformation**
- GID 805 `/Minimal Studio iPhone Candid` → **VARIANT: Candid Phone Photography**
- GID 1687 `/Minimalist Graphic Illustration of a Stylized Dachshund` → **VARIANT: Minimal Illustration**
- GID 763 `/Minimalist Landscape Illustration by Ryo Takemasa` → **VARIANT: Illustration Style**; rewrite away from living-artist imitation if necessary.
- GID 704 `/Mirror Product Photo` → **VARIANT: Product Photography**
- GID 2033 `/Mirror Selfie Scene Description` → **VARIANT: Candid Phone Photography**
- GID 1476 `/Mixed Media Portrait Illustration` → **VARIANT: Mixed-Media Portrait**
- GID 799 `/Museum Steps` → **VARIANT: Lifestyle/Travel Portrait**
- GID 1324 `/National Architecture Dioramas` → **VARIANT: Architectural Diorama**
- GID 873 `/Night Balcony Scene in Ankara with Efes` → **VARIANT: Night Lifestyle Scene**
- GID 795 `/Night Neon Alley` → **VARIANT: Neon/Cinematic Portrait**
- GID 800 `/Nightclub Booth Flash` → **VARIANT: Nightlife Candid**
- GID 1174 `/Nightclub Mirror Selfie` → **VARIANT: Nightlife Candid**
- GID 888 `/Ultra Realistic Bedroom Selfie Description` → **VARIANT: Candid Phone Photography**
- GID 1222 `/Ultra-Photorealistic Romantic Cinematic Scene in the Rain` → **VARIANT: Romantic Cinematic / Identity Lock**
- GID 881 `/Ultra-Realistic Ankara Apartment Night Scene` → **VARIANT: Night Lifestyle Scene**
- GID 872 `/Ultra-Realistic Ankara Indie Bar Scene Description` → **VARIANT: Night Lifestyle Scene**
- GID 886 `/Ultra-Realistic Ankara Street Photo with Surreal Element` → **VARIANT: Surreal Street Photography**
- GID 878 `/Ultra-Realistic Night Scene in a Turkish Kitchen` → **VARIANT: Night Lifestyle Scene**
- GID 1054 `/Ultra-Realistic Winter Cinematography Series` → **VARIANT: Winter Cinematic Series**
- GID 971 `/Ultra-Realistic Young Woman Portrait Generation` → **VARIANT: Photoreal Portrait**
- GID 1345 `/Valentines Day Cocktail` → **VARIANT: Product/Drink Video**
- GID 1372 `/Vibrant Fauvist Style Sunlit Living Room Illustration` → **VARIANT: Illustration Style**
- GID 1823 `/Video` → **VARIANT: Cinematic Product/Drink Video**
- GID 2103 `/Vintage copper engraving portrait with glasses in front of yellow circle` → **VARIANT: Vintage Engraving Portrait**
- GID 719 `/Vintage Invention Patent` → **VARIANT: Diagram / Patent Illustration**
- GID 1168 `/war` → **VARIANT: Historical Cinematic Scene**
- GID 834 `/Where the Kami Still Walk` → **VARIANT: Atmospheric Historical Scene**
- GID 589 `/World of Darkness B&W style` → **VARIANT: Comic / B&W Style**
- GID 592 `/World of Darkness Colored Comic style` → **VARIANT: Comic / Color Style**
- GID 806 `/Blue Hour Bridge` → **VARIANT: Blue-Hour Lifestyle Portrait**

## Remove from curated catalog

These do not justify a durable PromptDeck capability or are overly personal/one-off/corrupted:

- GID 1895 `/[sigrex.io] RSI + MACD Momentum` — named external service/trading workflow.
- GID 1301 `/A professional Egyptian barista` — one person's appliance/setup request; too specific to retain as a reusable card.
- GID 1275 `/Abandoned Wife` — bespoke character/scene payload, not reusable workflow.
- GID 1778 `/Alexa Said THIS… and Miss Nancy Didn’t Like It` — named-character content request.
- GID 1236 `/American Comic` — one-off story request rather than reusable comic-generation workflow.
- GID 2203 `/Attract Deer with Jangling Sounds` — narrow one-off informational request.
- GID 778 `/Automate Repository Management with OpenCode CLI` — external-tool/project-specific wrapper.
- GID 2206 `/Bamboo app` — named product + personal investment tutoring request; a general investing-learning capability is already better represented elsewhere.
- GID 1699 `/Ben` — custom persona.
- GID 1974 `/Bf` — one-off image edit request.
- GID 1432 `/Boom & Crush - ICT strategy` — narrow speculative trading request.
- GID 1800 `/Building a community` — fragment/statement, not a reusable prompt template.
- GID 1942 `/bulk images generate for black tshirt...` — one-off bulk generation request; product-photo capability already covers it.
- GID 1065 `/Cartoon series` — incomplete subject-specific request.
- GID 2190 `/Cat` — one-off story/video request.
- GID 131 `/Character` — novelty impersonation template.
- GID 279 `/Chemical Reactor` — simulation novelty with little practical value.
- GID 233 `/Chess Player` — game-opponent persona; if chess coaching is retained, keep a stronger analytical chess capability instead.
- GID 1736 `/mc` — cheating/hacking game request, not a useful curated workflow.
- GID 1781 `/MDCT Step-by-Step Calculation` — single solved-example request, not a reusable template.
- GID 1298 `/MeddaH` — language/persona-specific payload.
- GID 1358 `/Meme coins knowledge and trading` — vague personal request; no strong reusable prompt structure.
- GID 1471 `/National safety week` — dated one-off campaign request.
- GID 697 `/Nietzschean Mentor for Holistic Growth` — philosophy persona; underlying self-reflection capability is better represented elsewhere.
- GID 1966 `/Nigeria` — vague one-off country-problem request.
- GID 1871 `/Note` — vague, low-signal meta-instruction; superseded by stronger note/tutoring capabilities.
- GID 1663 `/Odalisque` — bespoke character payload.
- GID 2009 `/Oh` — one-off background edit request; merge intent into background-replacement family instead of keeping source card.
- GID 2121 `/Omniroute bulk input key converter (cf)` — named formatting workflow with possible sensitive-key handling; too specific.
- GID 1497 `/One-Shot Copy-Paste Version with Proper Formatting` — simple formatting preference already covered by output-format controls.
- GID 2020 `/nos` — fetishized explicit image request; remove.
- GID 1801 `/What friendship should be all about` — prose fragment, not reusable prompt.
- GID 484 `/worldquant` — non-English, platform-specific autonomous workflow.
- GID 354 `/Write Tier Descriptions` — GitHub Sponsors-specific microtask; fold into sponsorship/copywriting variants if needed.
- GID 2271 `/xiangxiang` — explicit sexual image prompt; remove.
- GID 851 `/Yağlı boya tablona bak` — non-English one-off visual request.
- GID 470 `/Патентный поиск` — non-English source item; do not surface in English-only catalog.

## Editorial consequence

The Specialist Roles bucket is structurally overloaded. Most entries are not true specialist-role capabilities; they are misplaced image prompts or one-off community requests. The category should shrink sharply and eventually contain only durable expert workflows such as accessibility audit, legal issue spotting, network troubleshooting, specialist review, and similar capabilities. Visual recipes should move to Photo/Image families, while generic utility transformations should move to their functional categories.

This pass is deliberately manual and title/GID-specific. It does not change production assets.