# Personalities

Each assistant personality lives in its own directory under `src/tur/personalities/`.

Each directory contains:

- `profile.yaml` for structured metadata
- one or more `.md` files containing reference material

Every text file in that directory other than `profile.yaml` is loaded as reference context for the personality's prompt.

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

1. Create a new directory in `src/tur/personalities/`.
2. Use the directory name as the personality key.
3. Add a `profile.yaml` file with the required fields.
4. Add any `.md` files you want the personality to use as standing reference material.
5. Start the app and switch with `/switch your_name`.

No code change should be required for normal personality additions.

## Existing Personalities

- `nina`: calm, grounded, quietly witty companion
- `tom`: calm, analytical, mechanically focused
- `tito`: energetic, concise, playful
- `asuka`: sharp, precise, assertive
