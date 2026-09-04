# PromptDeck Family Classification V4

Raw prompt cards: **3384**
Candidate multi-prompt families: **174**
MERGE families: **7**
VARIANT families: **70**
KEEP DISTINCT families: **97**
Entries removed by MERGE: **7**
Variant cards collapsed under a family card: **144**
Projected visible cards after family UI: **3233**

> Classification is intentionally conservative. MERGE is safe-delete territory; VARIANT means retain content under one discoverable family card; KEEP DISTINCT means do not collapse automatically.

## Facet architecture

### Photo Editing & Image Generation
- **Primary Intent**: Fix a photo · Improve a photo · Change the look · Create something new · Explore styles
- **Problem Or Goal**: Face & identity · Lighting · Color · Background · Quality & detail · Artifacts · Composition · Style transformation
- **Subject**: Person · Couple · Product · Landscape · Interior · Vehicle · Object
- **Look**: Natural · Editorial · Cinematic · Bright · Moody · Vintage · Minimal · Surreal
- **Preservation**: Keep identity · Keep composition · Keep clothing · Keep background · Free transformation

### Research & Analysis
- **Primary Intent**: Find · Verify · Understand · Compare · Investigate · Extract
- **Source**: Web · Social · Local · Files · Original source · Multiple sources
- **Depth**: Quick · Thorough · Deep hunt · Latest only
- **Evidence**: Facts · Consensus · Contradictions · Timeline · Source quality

### Writing & Rewriting
- **Primary Intent**: Write · Rewrite · Shorten · Expand · Clarify · Polish · Translate
- **Format**: Message · Email · Document · Post · Script · Summary
- **Tone**: Natural · Professional · Warm · Firm · Persuasive · Concise
- **Preservation**: Keep meaning · Match my voice · Fact-preserving

### Thinking & Ideas
- **Primary Intent**: Generate ideas · Decide · Challenge · Critique · Explore alternatives · Prioritize
- **Mode**: Divergent · Balanced · Skeptical · Second opinion · Pre-mortem
- **Output**: Best next move · Options · Decision tree · Trade-offs · Verdict

### Problem Solving & Technical
- **Primary Intent**: Build · Fix · Debug · Review · Test · Optimize · Explain
- **Domain**: Code · App/UI · API · Data · Security · Automation · Hardware
- **Depth**: Quick fix · Root cause · Architecture · Production-ready
- **Output**: Code · Plan · Checklist · Diagnosis · Review

### Business & Marketing
- **Primary Intent**: Sell · Market · Position · Plan · Analyze · Communicate
- **Area**: Sales · Marketing · SEO · Product · Customer · Strategy
- **Output**: Ideas · Campaign · Email · Plan · Comparison · Copy

### Learning & Study
- **Primary Intent**: Learn · Explain · Practice · Test me · Summarize · Plan study
- **Level**: Beginner · Intermediate · Advanced · Adaptive
- **Method**: 80/20 · Teach then test · Examples · Mental model · Quiz

### Planning & Execution
- **Primary Intent**: Plan · Prioritize · Schedule · Break down · Track
- **Horizon**: Now · Today · Week · Project · Long term
- **Output**: Next action · Checklist · Timeline · Roadmap

### Work & Career
- **Primary Intent**: Apply · Prepare · Write · Analyze · Plan · Communicate
- **Area**: CV · Interview · Email · Performance · Career decision · Meeting
- **Output**: Draft · Feedback · Plan · Questions · Summary

### Content Creation
- **Primary Intent**: Ideate · Create · Improve · Repurpose · Script · Package
- **Format**: Post · Video · Article · Caption · Story · Campaign
- **Style**: Educational · Entertaining · Persuasive · Editorial · Viral

### Lifestyle & Personal
- **Primary Intent**: Plan · Choose · Improve · Organize · Explore
- **Area**: Travel · Daily life · Relationships · Personal growth · Shopping
- **Output**: Ideas · Plan · Decision · Checklist

### AI & Prompting
- **Primary Intent**: Create prompt · Improve prompt · Build agent · Analyze prompt · Use AI better
- **Mode**: Single prompt · Workflow · Agent · Meta-prompt
- **Output**: Prompt · Framework · Instructions · Evaluation

### Data & Formatting
- **Primary Intent**: Extract · Transform · Format · Analyze · Convert
- **Input**: Text · Table · JSON · Spreadsheet · Document
- **Output**: Table · JSON · Structured text · Summary

### Health & Wellness
- **Primary Intent**: Understand · Prepare questions · Track · Plan · Compare
- **Area**: Symptoms · Fitness · Nutrition · Mental wellness · Appointments
- **Output**: Questions · Summary · Plan · Comparison

### Specialist Roles
- **Primary Intent**: Get expert perspective · Create · Analyze · Advise · Simulate
- **Output**: Advice · Draft · Analysis · Plan · Creative output

### Meta
- **Primary Intent**: Discover capabilities · Choose a prompt · Improve workflow

## Highest-confidence MERGE families

### /PowerShell Script to Move Disabled AD Users to Specific OU — 2 → 1 (high)
Reason: near-identical intent/body and strongly overlapping labels · mean sim 0.965 · title overlap 0.455
- /PowerShell Script to Move Disabled AD Users to Specific OU — community — q=4.084
- /PowerShell Script for Managing Disabled AD Users — community — q=3.415

### /Web Application Testing Skill — 2 → 1 (high)
Reason: near-identical intent/body and strongly overlapping labels · mean sim 0.994 · title overlap 1.0
- /Web Application Testing Skill — community — q=3.753
- /Web Application Testing Skill (Imported) — community — q=3.753

### /Senior Full-Stack Developer for Airline Simulation Center — 2 → 1 (high)
Reason: near-identical intent/body and strongly overlapping labels · mean sim 0.926 · title overlap 0.6
- /Senior Full-Stack Developer for Airline Simulation Center — community — q=3.287
- /Full-Stack Engineer for Airline Simulation Center App — community — q=2.942

### /Claude Code Skill (Slash Command): push-and-pull-request.md — 2 → 1 (high)
Reason: near-identical intent/body and strongly overlapping labels · mean sim 0.918 · title overlap 0.583
- /Claude Code Skill (Slash Command): push-and-pull-request.md — community — q=2.571
- /Claude Code Skill (Slash Command): review-and-commit.md — community — q=1.916

### /Comprehensive Book Summarizer — 2 → 1 (high)
Reason: near-identical intent/body and strongly overlapping labels · mean sim 0.847 · title overlap 1.0
- /Comprehensive Book Summarizer — community — q=2.207
- /Book Summarizer — community — q=1.571

### /Note-Taking assistant — 2 → 1 (high)
Reason: near-identical intent/body and strongly overlapping labels · mean sim 1.0 · title overlap 1.0
- /Note-Taking assistant — community — q=2.142
- /Note-Taking Assistant — community — q=2.142

### /Imported Prompt 2032 — 2 → 1 (high)
Reason: near-identical intent/body and strongly overlapping labels · mean sim 0.722 · title overlap 1.0
- /Imported Prompt 2032 — community — q=1.945
- /Imported Prompt 494 — community — q=0.655

## Largest VARIANT families

### /BoldSurrealInteriors — 11 variants
Reason: shared base capability with meaningful style/context differentiators · differentiators: abstractartisticsilhouette, abstractgeometricsurrealism, abstractsurrealportrait, boldsurrealinteriors, surrealcircularoceanview, surrealdoubleexposureportrait, surrealistcastlecloudscape, surrealistwatercomposition, surrealprimarystilllife, surrealunderwaterportrait, surrealvibrantfantasy
- /BoldSurrealInteriors — photo
- /SurrealUnderwaterPortrait — photo
- /SurrealPrimaryStillLife — photo
- /AbstractArtisticSilhouette — photo
- /SurrealistCastleCloudscape — photo
- /SurrealistWaterComposition — photo
- /SurrealCircularOceanView — photo
- /AbstractGeometricSurrealism — photo
- /SurrealVibrantFantasy — photo
- /SurrealDoubleExposurePortrait — photo
- /AbstractSurrealPortrait — photo

### /Museum Steps (full-body, cultural) — 9 variants
Reason: shared base capability with meaningful style/context differentiators · differentiators: alley, awkward, blue, body, booth, bridge, builder, but, candid, candids, candle, cinematic
- /Museum Steps (full-body, cultural) — community
- /Rooftop Sunset Lookback (half-body) — community
- /Rainy Umbrella Street (full-body) — community
- /Night Neon Alley (half-body, edgy) — community
- /Nightclub Booth Flash (half-body, party candids) — community
- /Tech Desk “Builder” (half-body, cozy monitor glow) — community
- /Restaurant Candle Close-up (intimate, not explicit) — community
- /Minimal Studio “iPhone Candid” (pro-quality but awkward framing) — community
- /“Blue Hour Bridge” (full-body, cinematic but still IG) — community

### /Comprehensive Code Review Expert — 7 variants
Reason: same functional neighborhood but differences may change the output · differentiators: review, reviewer
- /Comprehensive Code Review Expert — community
- /Code Review Specialist 2 — community
- /Code Review Professional — community
- /Code Review Specialist 3 — community
- /Code Review Expert — community
- /Code Review Specialist — community
- /Code Reviewer — community

### /EtherealNaturePortrait — 6 variants
Reason: shared base capability with meaningful style/context differentiators · differentiators: etherealfloralfilm, etherealinkdynamics, etherealnatureportrait, etherealpastellandscape, etherealunderwaterportrait, etherealwaterportrait
- /EtherealNaturePortrait — photo
- /EtherealInkDynamics — photo
- /EtherealFloralFilm — photo
- /EtherealWaterPortrait — photo
- /EtherealUnderwaterPortrait — photo
- /EtherealPastelLandscape — photo

### /Kitchen Morning Window Light (candid, cozy) — 5 variants
Reason: shared base capability with meaningful style/context differentiators · differentiators: aisle, artsy, balcony, bookstore, candid, coffee, colorful, cozy, farmers, haze, kitchen, light
- /Kitchen Morning Window Light (candid, cozy) — community
- /Bookstore Aisle (artsy, quiet luxury) — community
- /Balcony Coffee (morning haze, plant vibe) — community
- /Subway Platform (street candid, moody) — community
- /Farmers Market (colorful produce, candid) — community

### /Comic Book Team Illustration — 5 variants
Reason: shared base capability with meaningful style/context differentiators · differentiators: book, cinematic, close, comic, fauvist, generation, illustration, impressionistic, living, moonlit, portrait, room
- /Comic Book Team Illustration — community
- /Cinematic Close-Up Portrait Generation — community
- /Vibrant Fauvist Style Sunlit Living Room Illustration — community
- /Serene Moonlit Street Illustration — community
- /Impressionistic Urban Solitude — community

### /SEO Auditor Agent Role — 4 variants
Reason: same functional neighborhood but differences may change the output · differentiators: auditor, optimization, performance, seo, tuning
- /SEO Auditor Agent Role — community
- /SEO Optimization Agent Role — community
- /Optimization Auditor Agent Role — community
- /Performance Tuning Agent Role — community

### /PRD — 4 variants
Reason: shared base capability with meaningful style/context differentiators · differentiators: a, act, as, manager, prd, product, project
- /PRD — community
- /Act as a Product Manager — community
- /Project Manager — community
- /Product Manager — community

### /Good for us — 4 variants
Reason: shared base capability with meaningful style/context differentiators · differentiators: abandoned, cry, drunk, for, good, lonely, us, wife, woman
- /Good for us — community
- /Drunk Woman — community
- /Abandoned Wife — community
- /Lonely cry — community

### /Tropical Elegance: A Serene Afternoon in a Sunlit Villa — 4 variants
Reason: shared base capability with meaningful style/context differentiators · differentiators: afternoon, balcony, bed, chair, copper, decor, drenched, elegance, female, haired, in, light
- /Tropical Elegance: A Serene Afternoon in a Sunlit Villa — community
- /A relaxed copper-haired woman resting sideways on a bed in a soft, low-light setting. — community
- /A young woman relaxing in a wicker chair on a sunlit Mediterranean balcony. — community
- /Sun-Drenched Outdoor Selfie of a Tattooed Female Subject with Tiki Decor — community

### /Cinematic Photography Triptych: Serene Meadow Portrait — 4 variants
Reason: shared base capability with meaningful style/context differentiators · differentiators: a, art, artistic, cinematic, digital, dreamy, in, meadow, moody, neo, noir, of
- /Cinematic Photography Triptych: Serene Meadow Portrait — community
- /Cinematic Neo-Noir Triptych in Digital Art — community
- /Moody Cinematic Portrait Photography — community
- /Dreamy Artistic Photograph of a Young Woman in a Meadow — community

### /VividNatureLandscape — 4 variants
Reason: shared base capability with meaningful style/context differentiators · differentiators: dramaticautumnlandscape, infraredcolorizedlandscape, vibrantautumnlandscape, vividnaturelandscape
- /VividNatureLandscape — photo
- /InfraredColorizedLandscape — photo
- /VibrantAutumnLandscape — photo
- /DramaticAutumnLandscape — photo

### /VintageDesertElegance — 4 variants
Reason: shared base capability with meaningful style/context differentiators · differentiators: antiquewilderness, vintagecontemplativeportrait, vintagedesertelegance, vintagehorrorportrait
- /VintageDesertElegance — photo
- /AntiqueWilderness — photo
- /VintageHorrorPortrait — photo
- /VintageContemplativePortrait — photo

### /FoggyMinimalism — 4 variants
Reason: shared base capability with meaningful style/context differentiators · differentiators: foggyminimalism, minimalistblackandwhite, minimalistdesolatelandscape, minimalistfoggylandscape
- /FoggyMinimalism — photo
- /MinimalistBlackandWhite — photo
- /MinimalistFoggyLandscape — photo
- /MinimalistDesolateLandscape — photo

### /ExaggeratedVibrantFloralFantasyPortrait — 4 variants
Reason: shared base capability with meaningful style/context differentiators · differentiators: exaggeratedvibrantfloralfantasyportrait, floralfantasyportrait, vibrantfantasyportrait, vibrantfloralportrait
- /ExaggeratedVibrantFloralFantasyPortrait — photo
- /FloralFantasyPortrait — photo
- /VibrantFantasyPortrait — photo
- /VibrantFloralPortrait — photo

### /DramaticShadowandHighlightPortrait — 4 variants
Reason: shared base capability with meaningful style/context differentiators · differentiators: dramaticblackandwhiteportrait, dramaticshadowandhighlightportrait, dramaticspotlightheadshot, intensemonochromeportrait
- /DramaticShadowandHighlightPortrait — photo
- /IntenseMonochromePortrait — photo
- /DramaticSpotlightHeadshot — photo
- /DramaticBlackandWhitePortrait — photo

### /CleanProductShotonWhiteBackground — 4 variants
Reason: shared base capability with meaningful style/context differentiators · differentiators: backgroundreplacement, cleanproductshotonwhitebackground, greengradientbackgroundreplacement, purewhitebackgroundreplacement
- /CleanProductShotonWhiteBackground — photo
- /PureWhiteBackgroundReplacement — photo
- /GreenGradientBackgroundReplacement — photo
- /BackgroundReplacement — photo

### /Root Cause Analysis Agent Role — 3 variants
Reason: shared base capability with meaningful style/context differentiators · differentiators: analysis, analyst, bug, cause, error, handler, risk, root
- /Root Cause Analysis Agent Role — community
- /Bug Risk Analyst Agent Role — community
- /Error Handler Agent Role — community

### /Repository Indexer Agent Role — 3 variants
Reason: shared base capability with meaningful style/context differentiators · differentiators: editor, git, indexer, repository, workflow
- /Repository Indexer Agent Role — community
- /Git Workflow Expert Agent Role — community
- /Repository Workflow Editor Agent Role — community

### /Photorealistic Mirror Selfie Analysis — 3 variants
Reason: shared base capability with meaningful style/context differentiators · differentiators: a, aesthetic, analysis, bedroom, crop, curly, detailed, environment, haired, image, in, mocha
- /Photorealistic Mirror Selfie Analysis — community
- /Aesthetic Mirror Selfie of a Curly-Haired Woman in a Mocha Ribbed Crop Top — community
- /Detailed Image Analysis of a Mirror Selfie in a Bedroom Environment — community

### /Ultra-Realistic Ankara Street Photo with Surreal Element — 3 variants
Reason: shared base capability with meaningful style/context differentiators · differentiators: a, bar, description, element, in, indie, photo, realistic, scene, street, surreal, turkish
- /Ultra-Realistic Ankara Street Photo with Surreal Element — community
- /Turkish woman in Ankara with a surreal twist — community
- /Ultra-Realistic Ankara Indie Bar Scene Description — community

### /Develop a UI Library for ESP32 — 3 variants
Reason: shared base capability with meaningful style/context differentiators · differentiators: a, build, develop, development, for
- /Develop a UI Library for ESP32 — community
- /ESP32 UI Library Development — community
- /Build a UI Library for ESP32 — community

### /Serene Evening Rowboat Scene in Illustrative Realism — 3 variants
Reason: shared base capability with meaningful style/context differentiators · differentiators: autumn, boat, cinematic, evening, illustration, illustrative, in, lakeside, realism, rowboat, scene, serene
- /Serene Evening Rowboat Scene in Illustrative Realism — community
- /Cinematic Sunset Boat Scene — community
- /Serene Autumn Lakeside Illustration — community

### /emails Professionals — 3 variants
Reason: same functional neighborhood but differences may change the output · differentiators: an, any, email, emails, for, occasion, professionals, write, writer
- /emails Professionals — community
- /Professional Email Writer for Any Occasion — community
- /Write an Email — community

### /Ankara Night Scene in a Meyhane — 3 variants
Reason: shared base capability with meaningful style/context differentiators · differentiators: a, ankara, cozy, during, football, in, living, match, meyhane, night, realistic, room
- /Ankara Night Scene in a Meyhane — community
- /Ultra-Realistic Turkish Living Room Scene During Football Match — community
- /Cozy Night in Ankara: A Turkish TV Series Snapshot — community

### /Night Balcony Scene in Ankara with Efes — 3 variants
Reason: shared base capability with meaningful style/context differentiators · differentiators: a, apartment, balcony, bedroom, capturing, cozy, efes, in, realistic, ultra, with
- /Night Balcony Scene in Ankara with Efes — community
- /Ultra-Realistic Ankara Apartment Night Scene — community
- /Cozy Ankara Night: Capturing a Realistic Bedroom Scene — community

### /Detailed Image Generation Prompt for Fashion and Portrait Photography — 3 variants
Reason: shared base capability with meaningful style/context differentiators · differentiators: and, bikini, detailed, fashion, for, generation, image, photography, portrait, prompt, with, woman
- /Detailed Image Generation Prompt for Fashion and Portrait Photography — community
- /Womanized — community
- /Young woman with bikini — community

### /Minimalist Editorial Beauty Analysis with European Model — 3 variants
Reason: shared base capability with meaningful style/context differentiators · differentiators: asian, east, european, turkish
- /Minimalist Editorial Beauty Analysis with European Model — community
- /Minimalist Editorial Beauty Analysis with Turkish Model — community
- /Minimalist Editorial Beauty Analysis with East Asian Model — community

### /Reply-Focused Cold Email Builder — 3 variants
Reason: shared base capability with meaningful style/context differentiators · differentiators: builder, focused, outreach, reply
- /Reply-Focused Cold Email Builder — community
- /Cold outreach email — pdf
- /Cold email — pdf

### /SunsetMeadowDreamscape — 3 variants
Reason: shared base capability with meaningful style/context differentiators · differentiators: afterdusknorthernlandscape, duskfantasyteenportrait, sunsetmeadowdreamscape
- /SunsetMeadowDreamscape — photo
- /AfterDuskNorthernLandscape — photo
- /DuskFantasyTeenPortrait — photo

### /Git Repository Analysis and Knowledge Base Construction — 3 variants
Reason: shared base capability with meaningful style/context differentiators · differentiators: analysis, and, base, construction, deep, enhancement, git, github, knowledge, understanding
- /Git Repository Analysis and Knowledge Base Construction — community
- /GitHub Repository Analysis and Enhancement — community
- /Deep GitHub Repository Understanding — community

### /CinematicNoirWindowPortrait — 3 variants
Reason: shared base capability with meaningful style/context differentiators · differentiators: cinematiclakeportrait, cinematicnighttimeurbanportrait, cinematicnoirwindowportrait
- /CinematicNoirWindowPortrait — photo
- /CinematicNighttimeUrbanPortrait — photo
- /CinematicLakePortrait — photo

### /OrnatePortrait — 3 variants
Reason: shared base capability with meaningful style/context differentiators · differentiators: ornateportrait, pastelclassicportrait, vibrantfashionportrait
- /OrnatePortrait — photo
- /PastelClassicPortrait — photo
- /VibrantFashionPortrait — photo

### /DynamicCloseUpMovement — 3 variants
Reason: shared base capability with meaningful style/context differentiators · differentiators: dynamiccloseupmovement, dynamicmonochromewithredaccent, macrovibrantfantasynature
- /DynamicCloseUpMovement — photo
- /MacroVibrantFantasyNature — photo
- /DynamicMonochromewithRedAccent — photo

### /IndigenousAfricanDuskPortrait — 3 variants
Reason: shared base capability with meaningful style/context differentiators · differentiators: africanartportrait, indigenousafricanduskportrait, vibrantafricandocumentaryportrait
- /IndigenousAfricanDuskPortrait — photo
- /AfricanArtPortrait — photo
- /VibrantAfricanDocumentaryPortrait — photo

### /DoubleExposureNaturePortrait — 3 variants
Reason: shared base capability with meaningful style/context differentiators · differentiators: doubleexposurecolorportrait, doubleexposurenatureportrait, vibrantdoubleexposureportrait
- /DoubleExposureNaturePortrait — photo
- /VibrantDoubleExposurePortrait — photo
- /DoubleExposureColorPortrait — photo

### /Video Cinematográfico IA | Agente Celestial Designs — 3 variants
Reason: shared base capability with meaningful style/context differentiators · differentiators: 8k, cinematogr, dise, fi, fico, hud, ia, o, realismo, sci, video
- /Video Cinematográfico IA | Agente Celestial Designs — community
- /Diseño HUD Sci-Fi | Agente Celestial Designs — community
- /Realismo Cinematográfico 8K | Agente Celestial Designs — community

### /Digital product ideas — 3 variants
Reason: shared base capability with meaningful style/context differentiators · differentiators: automation, digital, for, ideas, product, sales, selar
- /Digital product ideas — community
- /Sales — community
- /Selar ideas for automation — community

### /Code Reviewer Agent Role — 2 variants
Reason: same functional neighborhood but differences may change the output · differentiators: review, reviewer
- /Code Reviewer Agent Role — community
- /Code Review Agent Role — community

### /Prompt Engineering Expert — 2 variants
Reason: same functional neighborhood but differences may change the output · differentiators: architect, engineering, pro
- /Prompt Engineering Expert — community
- /Prompt Architect Pro — community

### /DiComPress Ω — Dual-Language Semantic Hypercompressor — 2 variants
Reason: same functional neighborhood but differences may change the output · differentiators: compressor, hypercompressor
- /DiComPress Ω — Dual-Language Semantic Hypercompressor — community
- /DiComPress: Dual-Language Semantic Compressor — community

### /Functional Analyst — 2 variants
Reason: same functional neighborhood but differences may change the output · differentiators: mode, small
- /Functional Analyst — community
- /Small Functional Analyst mode — community

### /Apple App Store Review Compliance Agent — 2 variants
Reason: same functional neighborhood but differences may change the output · differentiators: apple, compliance, review, submission
- /Apple App Store Review Compliance Agent — community
- /App Store Submission Agent — community

### /Investigative Research Assistant for Uncovering Non-Mainstream Information — 2 variants
Reason: same functional neighborhood but differences may change the output · differentiators: for, information, mainstream, non, uncovering
- /Investigative Research Assistant for Uncovering Non-Mainstream Information — community
- /Investigative Research Assistant — community

### /Ultimate Stake.us Dice Wagering Strategy Builder — Rollover & Playthrough Completion — 2 variants
Reason: same functional neighborhood but differences may change the output · differentiators: all, bankrolls, completion, levels, playthrough, risk, rollover, wagering
- /Ultimate Stake.us Dice Wagering Strategy Builder — Rollover & Playthrough Completion — community
- /Ultimate Stake.us Dice Strategy Builder — All Risk Levels & Bankrolls — community

### /Literature Reading Assistant — 2 variants
Reason: same functional neighborhood but differences may change the output · differentiators: analysis, and
- /Literature Reading Assistant — community
- /Literature Reading and Analysis Assistant — community

### /Generate a Plan for Building the Best UI/UX — 2 variants
Reason: same functional neighborhood but differences may change the output · differentiators: a, already, an, application, better, building, created, for, generate, make, of, plan
- /Generate a Plan for Building the Best UI/UX — community
- /Make UI/UX better of an already Created Application — community

### /Sports Events Weekly Listings Prompt — 2 variants
Reason: same functional neighborhood but differences may change the output · differentiators: games, olympic, sports
- /Sports Events Weekly Listings Prompt — community
- /Olympic Games Events Weekly Listings Prompt — community

### /Birthday Message Generator – 3 Styles — 2 variants
Reason: same functional neighborhood but differences may change the output · differentiators: customizable, styles
- /Birthday Message Generator – 3 Styles — community
- /Customizable Birthday Message Generator — community

### /Open Source / Free License Selection Assistant — 2 variants
Reason: same functional neighborhood but differences may change the output · differentiators: free, from, intellectual, open, property, source
- /Open Source / Free License Selection Assistant — community
- /License Selection Assistant from Intellectual Property expert — community

### /Accessibility Expert — 2 variants
Reason: same functional neighborhood but differences may change the output · differentiators: superpower, testing
- /Accessibility Expert — community
- /Accessibility Testing Superpower — community

### /Vibe Coding Master — 2 variants
Reason: same functional neighborhood but differences may change the output · differentiators: and, commands, master, skills, with
- /Vibe Coding Master — community
- /Vibe Coding with Commands and Skills — community

### /Android Update Checker Script for Pydroid 3 — 2 variants
Reason: same functional neighborhood but differences may change the output · differentiators: android, for, pydroid, script
- /Android Update Checker Script for Pydroid 3 — community
- /Update checker — community

### /Detailed mirror-selfie room scene — 2 variants
Reason: same functional neighborhood but differences may change the output · differentiators: description, detailed, room
- /Detailed mirror-selfie room scene — community
- /Mirror Selfie Scene Description — community

### /Creating a Comprehensive Elasticsearch Search Project with FastAPI — 2 variants
Reason: same functional neighborhood but differences may change the output · differentiators: and, building, creating, elasticsearch, postgresql, project, scalable, service
- /Creating a Comprehensive Elasticsearch Search Project with FastAPI — community
- /Building a Scalable Search Service with FastAPI and PostgreSQL — community

### /[sigrex.io] Full Kitchen Sink — 2 variants
Reason: same functional neighborhood but differences may change the output · differentiators: fear, filter, full, greed, kitchen, sentiment, sink
- /[sigrex.io] Full Kitchen Sink — community
- /[sigrex.io] Fear & Greed Sentiment Filter — community

### /Seaside walker — 2 variants
Reason: same functional neighborhood but differences may change the output · differentiators: bikini, girl, seaside, walker
- /Seaside walker — community
- /Bikini_Girl — community

### /Compare Top Virtualization Solutions — 2 variants
Reason: same functional neighborhood but differences may change the output · differentiators: compare, solutions, top
- /Compare Top Virtualization Solutions — community
- /Virtualization Expert — community

### /3D Isometric Miniature City View with Weather — 2 variants
Reason: same functional neighborhood but differences may change the output · differentiators: cartoon, scene, view, weather, with
- /3D Isometric Miniature City View with Weather — community
- /Isometric miniature 3D cartoon city scene — community

### /Hypnotherapist Guidance for Stress Management — 2 variants
Reason: same functional neighborhood but differences may change the output · differentiators: for, guidance, management, stress
- /Hypnotherapist Guidance for Stress Management — community
- /Hypnotherapist — community

### /Professional Badge Photo, Ready to Use — 2 variants
Reason: same functional neighborhood but differences may change the output · differentiators: badge, image, photo, ready, to, use
- /Professional Badge Photo, Ready to Use — community
- /Image — community

### /World of Darkness Colored Comic style — 2 variants
Reason: same functional neighborhood but differences may change the output · differentiators: b, colored, comic, w
- /World of Darkness Colored Comic style — community
- /World of Darkness B&W style — community

### /Prompt Enhancer (concise) — 2 variants
Reason: same functional neighborhood but differences may change the output · differentiators: concise
- /Prompt Enhancer (concise) — community
- /Prompt Enhancer — community

### /Movie Critic — 2 variants
Reason: same functional neighborhood but differences may change the output · differentiators: film, movie
- /Movie Critic — community
- /Film Critic — community

### /Chinese to English Translation Assistant — 2 variants
Reason: same functional neighborhood but differences may change the output · differentiators: proofreading
- /Chinese to English Translation Assistant — community
- /Chinese to English Translation Proofreading Expert — community

### /Create a study plan — 2 variants
Reason: same functional neighborhood but differences may change the output · differentiators: a, create
- /Create a study plan — pdf
- /Study plan — pdf

### /Hyperrealistic Food Video Creator — 2 variants
Reason: same functional neighborhood but differences may change the output · differentiators: photo, video
- /Hyperrealistic Food Video Creator — community
- /Hyperrealistic Food Photo Creator — community

### /Act as a travel planner. Build a [days]-day itinerary for [destination — 2 variants
Reason: same functional neighborhood but differences may change the output · differentiators: build, design, family, for, itinerary, to, travel, trip
- /Act as a travel planner. Build a [days]-day itinerary for [destination — pdf
- /Act as a family-trip planner. Design a [days]-day trip to [destination — pdf

### /Act as a fitness-goal planner. Turn '[vague goal]' into a specific, me — 2 variants
Reason: same functional neighborhood but differences may change the output · differentiators: fitness, health, me, mea
- /Act as a fitness-goal planner. Turn '[vague goal]' into a specific, me — pdf
- /Act as a health-goal planner. Turn '[vague goal]' into a specific, mea — pdf

### /Cocktail videos — 2 variants
Reason: same functional neighborhood but differences may change the output · differentiators: cocktail, video, videos
- /Cocktail videos — community
- /Video — community
