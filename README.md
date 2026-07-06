# tur.ai

`tur.ai` is the software foundation for an AI operating system for motorcycles.

Sprint 0 focuses on one thing: a clean, maintainable architecture for a terminal-based assistant running on a laptop. It does not attempt to ship voice, Raspberry Pi integration, Bluetooth, GPS, Spotify, or diagnostics yet. The codebase is structured so those capabilities can be added later without rewriting the core assistant.

## Current Scope

- Terminal chat loop
- Personality-driven assistant behavior
- Swappable LLM interface
- JSON-backed memory abstraction
- Environment-based configuration
- Modular package layout for future expansion

## Project Layout

```text
tur-ai/
├── README.md
├── LICENSE
├── requirements.txt
├── .env.example
├── .gitignore
├── docs/
│   ├── architecture.md
│   ├── personalities.md
│   └── roadmap.md
├── scripts/
├── src/
│   └── tur/
│       ├── assistant/
│       ├── config/
│       ├── llm/
│       ├── memory/
│       ├── personalities/
│       ├── services/
│       ├── utils/
│       └── main.py
└── tests/
```

## Architecture

The core flow is intentionally narrow:

```text
Terminal UI
    ↓
AssistantManager
    ↓
PromptBuilder + MemoryStore + PersonalityRegistry
    ↓
LLMClient interface
    ↓
OpenAI provider
```

This keeps OpenAI-specific code isolated behind a provider boundary and prevents the rest of the application from coupling directly to one SDK or one storage format.

## Setup

1. Create and activate a virtual environment:

   ```bash
   python3.12 -m venv .venv
   source .venv/bin/activate
   ```

2. Install dependencies:

   ```bash
   python3.12 -m pip install -r requirements.txt
   ```

3. Configure environment variables:

   ```bash
   cp .env.example .env
   ```

4. Add your OpenAI API key to `.env`:

   ```env
   OPENAI_API_KEY=your_key_here
   ```

5. Run the assistant:

   ```bash
   PYTHONPATH=src python3.12 -m tur.main
   ```

If `OPENAI_API_KEY` is not configured, the app falls back to a development LLM client so the architecture and terminal workflow can still be exercised locally.

## Terminal Commands

- `/switch tom`
- `/switch karen`
- `/switch asuka`
- `/switch tito`
- `/memory`
- `/remember I own a Ninja 400.`
- `/help`
- `/quit`

## Testing

Run the test suite with:

```bash
PYTHONPATH=src python3.12 -m pytest
```

## Roadmap

Sprint 0 establishes the foundation for:

- voice input and text-to-speech
- wake phrase detection
- Raspberry Pi deployment
- Bluetooth accessory control
- Spotify integration
- GPS and ride-aware context
- bike diagnostics and telemetry
- richer memory backends
- multiple LLM providers

See [docs/roadmap.md](/home/tura/turai/docs/roadmap.md) and [docs/architecture.md](/home/tura/turai/docs/architecture.md) for details.

## Design Principles

- Keep interfaces explicit and small.
- Separate behavior from infrastructure.
- Prefer composition over global state.
- Treat personalities, memory, and providers as pluggable modules.
- Optimize for long-term maintainability over short-term convenience.
