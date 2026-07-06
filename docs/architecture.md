# Architecture

## Goals

Sprint 0 prioritizes clear boundaries over feature breadth. The assistant is intentionally split into modules that can evolve independently as `tur.ai` grows into a motorcycle-focused operating system.

## Core Components

### Terminal Interface

`src/tur/services/terminal_chat.py` owns the command loop and terminal interaction. It is deliberately thin and delegates assistant behavior to domain services.

### Assistant Manager

`src/tur/assistant/manager.py` coordinates personalities, prompt construction, memory access, and LLM responses. It acts as the application orchestration layer.

### Personality Registry

`src/tur/personalities/loader.py` loads YAML personality files from disk and converts them into typed domain objects. Adding a new personality should only require adding a new YAML file.

### Memory Store

`src/tur/memory/base.py` defines the memory interface. `src/tur/memory/json_store.py` provides the Sprint 0 implementation. The assistant does not know whether memory comes from JSON, SQLite, or a vector store.

### Environment Store

`src/tur/environment/base.py` defines a lightweight world-state interface. `src/tur/environment/json_store.py` stores recent ambient events such as what a personality was recently discussing with Gio. This lets personalities reference recent activity naturally without talking about shared memory mechanics.

### Presence State

`src/tur/environment/presence_store.py` persists lightweight per-personality presence such as current focus and background activity. This is intentionally shallow and heuristic-driven so it adds continuity without adding expensive generation or retrieval steps.

### LLM Layer

`src/tur/llm/base.py` defines the LLM interface. `src/tur/llm/openai_client.py` contains the OpenAI SDK integration. `src/tur/llm/development_client.py` exists to keep the app runnable without credentials while preserving the abstraction.

## Dependency Direction

Dependencies point inward:

- services depend on assistant orchestration
- assistant orchestration depends on interfaces and domain models
- infrastructure modules implement those interfaces

This keeps future changes local. For example, adding a Bluetooth service or a second LLM provider should not force changes across unrelated modules.

## Future Extensions

The current structure is designed to absorb:

- voice input and wake-word listeners as new services
- text-to-speech as an output adapter
- SQLite or vector memory backends behind the existing memory interface
- provider selection for Anthropic, local models, or other LLMs
- ride context ingestion through GPS, diagnostics, and device APIs
