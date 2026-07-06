# Personalities

Each assistant personality lives in `src/tur/personalities/` as a standalone YAML file.

## Required Fields

- `name`
- `description`
- `system_prompt`
- `wake_phrase`
- `sleep_phrase`
- `speaking_style`
- `humor_level`
- `verbosity`

## Adding a Personality

1. Create a new YAML file in `src/tur/personalities/`.
2. Use the filename stem as the personality key.
3. Fill in all required fields.
4. Start the app and switch with `/switch your_name`.

No code change should be required for normal personality additions.

## Existing Personalities

- `karen`: direct, practical, lightly witty
- `tom`: calm, analytical, mechanically focused
- `tito`: energetic, concise, playful
- `asuka`: sharp, precise, assertive
