# PromptDeck v0.2.0

Small Android prompt-composer app. It turns reusable prompt operators into one ordered, coherent prompt and sends it to ChatGPT using Android sharing.

## v0.2.0
- 120 built-in prompt operators (96 original + 24 additional reasoning/decision/coding/planning operators).
- Add custom prompt operators directly inside the app.
- Delete custom operators.
- Import prompt packs from JSON.
- Export all custom operators to a portable `.promptdeck.json` file.
- No account, backend, API key, or network permission.

## Import format
Recommended file extension: `.promptdeck.json`

```json
{
  "format": "promptdeck-pack",
  "version": 1,
  "name": "My Prompt Operators",
  "commands": [
    {
      "command": "rootcause",
      "category": "Reasoning",
      "description": "يدور على السبب الجذري",
      "instruction": "Perform root-cause analysis..."
    }
  ]
}
```

The importer also accepts a bare JSON array of command objects or one single command object. `command` and `instruction` are required. `category` and `description` are optional.

Important: these slash names are PromptDeck shortcuts, not native ChatGPT slash commands. PromptDeck expands each one into an instruction before sharing the final prompt.
