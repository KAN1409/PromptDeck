# PromptDeck Full Library Triage V1

Source of truth: exported app catalog, **3,409 prompts**.

## Confirmed findings

- 5 exact duplicate instruction groups (5 safely removable duplicate records, keeping one canonical record per group).
- 1 additional normalized near-exact group requiring a quick human check.
- 1 command-name collision group.
- 35 category labels exist in the export; 120 records still use legacy category labels.
- 104 prompts exceed 10,000 characters; 5 exceed 50,000; maximum is 136,835.
- 65 source-dump / oversized-skill review candidates using conservative markers.
- Non-English script hits: Arabic 18, Cyrillic 4, CJK 21, Hebrew 1.

## Exact duplicate groups

- `ProfessionalBadgePhotoReadytoUse` (ID 30311) ↔ `Image` (ID 32033)
- `Sales` (ID 30317) ↔ `Selarideasforautomation` (ID 30319)
- `UltraRealisticNoirPortraitCreation` (ID 30318) ↔ `Ainew` (ID 30359)
- `Seasidewalker` (ID 30958) ↔ `BikiniGirl` (ID 31586)
- `Cocktailvideos` (ID 31178) ↔ `Video` (ID 31702)

## Command collision

- `explain`: `explain` ID 11 (`Explain`) ↔ `explain` ID 50 (`Research`)

## Legacy category normalization

- `Writing` → `Writing & Rewriting` (13 records)
- `Transform` → `Writing & Rewriting` (6 records)
- `Explain` → `Learning & Study` (5 records)
- `Ideation` → `Thinking & Ideas` (3 records)
- `Content` → `Content Creation` (9 records)
- `Planning` → `Planning & Execution` (12 records)
- `Analysis` → `Research & Analysis` (10 records)
- `Decision` → `Thinking & Ideas` (9 records)
- `Study` → `Learning & Study` (9 records)
- `Research` → `Research & Analysis` (7 records)
- `Work` → `Work & Career` (7 records)
- `Career` → `Work & Career` (3 records)
- `Technical` → `Problem Solving & Technical` (3 records)
- `Coding` → `Problem Solving & Technical` (4 records)
- `Format` → `Data & Formatting` (6 records)
- `Data` → `Data & Formatting` (3 records)
- `Reasoning` → `Thinking & Ideas` (6 records)
- `Quality` → `Thinking & Ideas` (2 records)
- `Evaluation` → `Thinking & Ideas` (2 records)
- `Meta` → `AI & Prompting` (1 record)

## Other-model references — review for ChatGPT suitability

- Claude: 74
- Gemini: 45
- Cursor: 13
- Copilot: 18
- MCP: 15
- Anthropic: 21
- Codex: 8
- Windsurf: 2
- OpenCode: 1
- Perplexity: 9

These are review signals, not automatic removals. A tool-specific prompt may still be useful if the capability is relevant to ChatGPT, but prompts whose instructions only make sense inside another assistant or coding-agent runtime should not survive unchanged.

## Highest-risk source-dump / oversized candidates

- ID 30994 `MCPBuilder` — 102,198 chars, marker score 5
- ID 31100 `skillmaster` — 47,050 chars, marker score 4
- ID 31030 `GitHubTrends` — 43,154 chars, marker score 4
- ID 32055 `UniversalInstructionsforReactNextjsPro` — 22,116 chars, marker score 4
- ID 31380 `UpdateAgentPermissions` — 2,706 chars, marker score 4
- ID 31184 `SocraticLens` — 136,835 chars, marker score 3
- ID 31302 `MinimaxMusicLyricsGeneration` — 48,956 chars, marker score 3
- ID 31099 `claudemdmaster` — 44,496 chars, marker score 3
- ID 30918 `Context7DocumentationExpertAgent` — 25,194 chars, marker score 3
- ID 31174 `PromptEngineeringExpert` — 67,091 chars, marker score 2
- ID 32056 `Exuvia` — 24,787 chars, marker score 2
- ID 32007 `CodebaseEcosystemAtlas` — 21,178 chars, marker score 2
- ID 31096 `TheUltimateTypeScriptCodeReview` — 20,911 chars, marker score 2
- ID 31511 `RepositoryIndexerAgentRole` — 20,727 chars, marker score 2
- ID 31434 `DesignHandoffNotesAIFirstHumanReadable` — 18,706 chars, marker score 2
- ID 30998 `SkillCreator` — 18,552 chars, marker score 2
- ID 30409 `Comprehensiverepositoryanalysis` — 16,070 chars, marker score 2
- ID 30961 `CommitMessagePreparation` — 13,474 chars, marker score 2
- ID 30619 `AccessibilityTestingSuperpower` — 7,856 chars, marker score 2
- ID 30915 `VSCodeCodeTourExpertAgent` — 6,753 chars, marker score 2
- ID 30616 `ASTCodeAnalysisSuperpower` — 6,231 chars, marker score 2
- ID 31378 `trellointegrationskill` — 5,829 chars, marker score 2
- ID 31443 `RepositorySecurityArchitectureAuditFra` — 5,611 chars, marker score 2
- ID 31114 `ClaudeCodeStatuslineDesign` — 3,949 chars, marker score 2
- ID 31319 `AdvancedSalesFunnelAppwithReactFlow` — 2,339 chars, marker score 2
- ID 30695 `CodebaseWIKIDocumentationSkill` — 1,687 chars, marker score 2
- ID 32154 `ExpertLensLite` — 77,501 chars, marker score 1
- ID 31560 `baseR` — 67,255 chars, marker score 1
- ID 31395 `ComprehensivePythonCodebaseReviewForen` — 34,491 chars, marker score 1
- ID 31394 `ComprehensiveGoCodebaseReviewForensicL` — 34,102 chars, marker score 1
- ID 30712 `HouseholdMaintenanceSafetyAssistant` — 32,384 chars, marker score 1
- ID 32006 `GoIndustrialAutonomousBusinessModuleCo` — 30,256 chars, marker score 1
- ID 31097 `PHPMicroscopeForensicCodebaseAutopsyPr` — 29,485 chars, marker score 1
- ID 31755 `LeadGeneratorTrackerWordPilotpro` — 27,481 chars, marker score 1
- ID 32128 `JobRiskIntelligenceAnalyzer` — 26,184 chars, marker score 1
- ID 31758 `EmailLeadGeneratorTracker` — 24,495 chars, marker score 1
- ID 31510 `DeepResearchAgentRole` — 21,955 chars, marker score 1
- ID 31501 `PostImplementationAuditAgentRole` — 21,240 chars, marker score 1
- ID 31645 `XTwitterScraper` — 21,239 chars, marker score 1
- ID 31512 `VisualMediaAnalysisExpertAgentRole` — 20,624 chars, marker score 1

## Editorial rule

Similarity is retrieval assistance only. Preserve distinct capabilities and meaningful variants. Remove only confirmed duplicates, broken imports, or prompts that are clearly inferior/redundant after semantic review. Long prompts may be valid agent/skill prompts; length alone is never a removal rule. High lexical similarity among templated photo prompts is not evidence of duplication.