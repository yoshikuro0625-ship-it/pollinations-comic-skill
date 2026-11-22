---
name: pollinations-comic
description: Turn one sentence into a 4-panel comic strip with Pollinations models. Use when the user wants a comic, a storyboard, or a short illustrated story made from a theme, a character, or a joke. Generates the script with a text model, draws the panels with an image model, and assembles a 2x2 strip.
allowed-tools: Bash(polli *), Bash(python3 *)
---

# pollinations-comic — one sentence, four panels

Turn a single idea into a finished 4-panel comic strip, end to end, using only Pollinations models through the `polli` CLI. The user never handles an API key: `polli auth login` signs the agent in once, and every generation spends from the user's own Pollinations balance (Pollinations Pay).

## Setup (once)

```bash
npm i -g @pollinations/cli@latest
polli auth login          # approve in the browser; tokens stay local
polli usage               # check the balance before a big run
```

If `polli` is missing, install it first. Never ask the user to paste an API key into chat.

## Workflow

1. **Get the theme.** One sentence from the user, for example "a cat astronaut who is afraid of heights". If they give no theme, ask for one.
2. **Write the script.** One text-model call returns strict JSON: a title plus four panels, each with an `image_prompt` (visual description, same characters and style in every panel) and a short `caption` (one line of dialogue or narration).

```bash
polli gen text --model openai/gpt-5.4-nano --json-response --max-tokens 600 \
  "Write a 4-panel comic script about: THEME. Return only JSON: {\"title\": \"...\", \"panels\": [{\"image_prompt\": \"...\", \"caption\": \"...\"}, x4]}. Keep the same characters, setting and art style in all four image prompts. Captions are one short line each."
```

3. **Draw the panels.** One image-model call per panel, same seed base so the style holds together. Use a model that accepts the user's balance type: `black-forest-labs/flux.1-schnell` is cheap and is not paid-only, so quest balance covers it. Default image model `zimage` works too.

```bash
polli gen image --model black-forest-labs/flux.1-schnell \
  --width 768 --height 768 --seed 42 \
  --output panel1.png "PANEL_1_IMAGE_PROMPT, flat comic style, bold outlines"
```

4. **Assemble the strip.** Run the bundled script, which lays the four panels out 2x2 with caption bars and writes the finished strip plus `panels.json`.

```bash
python3 scripts/comic.py --theme "THEME" --out ./my-comic
```

Or run the script with `--script panels.json` to reuse a script you already have. The script calls the same `polli` commands above, so steps 2-4 happen in one run.

## Cost (measured 2026-11-22)

- Script (text model): about $0.0002.
- Four panels (FLUX.1 Schnell): about $0.008 in total.
- A whole strip costs roughly one cent from quest balance. Paid-only models cost more and cannot be paid with quest balance, so stay on the models named here unless the user asks otherwise.

## Rules

- Keep the same characters, setting and art style in all four `image_prompt` values, or the strip falls apart panel to panel.
- Captions stay one line each. If a caption comes back long, shorten it instead of shrinking the font.
- Japanese captions need a CJK font. Pass `--font` with a path to a font such as Noto Sans JP; without one, captions fall back to the default bitmap font and Japanese glyphs will not render.
- Show the finished strip to the user before offering variations. Offer a new seed or a rewritten panel, not a whole new strip, unless they ask for one.

## Files

- `scripts/comic.py` — the whole pipeline: script, panels, strip.
- `examples/demo-strip.png` — a strip made with this skill (theme: a cat astronaut afraid of heights).
