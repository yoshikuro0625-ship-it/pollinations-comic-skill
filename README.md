# pollinations-comic — an agent skill that makes comics with Pollinations

[![Made with pollinations.ai](https://raw.githubusercontent.com/pollinations/pollinations/main/packages/ui/src/brand/badge-made-with.svg)](https://pollinations.ai/?ref=badge)

One sentence in, a finished 4-panel comic strip out. A text model writes the
script, an image model draws the four panels, and `scripts/comic.py` assembles
the strip. Everything runs through the `polli` CLI, so the user signs in once
with `polli auth login` and generations spend from their own Pollinations
balance (Pollinations Pay). No API key is handled by the skill.

## Try it

```bash
npm i -g @pollinations/cli@latest
polli auth login
python3 scripts/comic.py --theme "a cat astronaut who is afraid of heights" --out ./my-comic
```

The finished strip is `my-comic/strip.png`. One strip costs about $0.01 from
quest balance with the default models (measured 2026-11-22).

## Files

- `SKILL.md` — the agent skill (Agent Skills format).
- `scripts/comic.py` — the whole pipeline: script, panels, strip.
- `examples/demo-strip.png` — a strip made with this skill.

## Submit for quest #20020

This skill was built for Pollinations quest
[#20020](https://github.com/pollinations/pollinations/issues/20020)
("An agent skill that makes something creative with Pollinations", $10 in
quest balance). To submit it:

1. Put this folder in your own public GitHub repository.
2. Open the
   [app submission form](https://github.com/pollinations/pollinations/issues/new?template=app-submission.yml),
   enter `#20020` in its **Quest** field, and leave the App URL empty.
3. When a maintainer approves the submission it joins the app catalog, the
   quest closes, and the reward can be claimed at
   https://enter.pollinations.ai/quests.
