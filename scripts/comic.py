#!/usr/bin/env python3
"""pollinations-comic: one sentence -> 4-panel comic strip.

Pipeline: polli gen text (script, JSON) -> polli gen image x4 (panels)
-> Pillow 2x2 strip with caption bars.

Auth comes from the polli CLI (polli auth login); this script never touches
an API key. Generation spends from the user's own Pollinations balance
(Pollinations Pay). Default models are not paid-only, so quest balance
covers a strip (measured 2026-11-22: about $0.01 per strip).

Usage:
  python3 comic.py --theme "a cat astronaut who is afraid of heights" --out ./my-comic
  python3 comic.py --theme "..." --out ./my-comic --font /path/to/NotoSansJP-Regular.ttf
  python3 comic.py --script panels.json --out ./my-comic   # reuse a script
"""
import argparse
import json
import os
import subprocess
import sys

TEXT_MODEL = "openai/gpt-5.4-nano"
IMAGE_MODEL = "black-forest-labs/flux.1-schnell"
PANEL_W, PANEL_H = 768, 768
CAPTION_H = 64
GAP = 16


def run(cmd, **kw):
    print("+", " ".join(cmd), flush=True)
    r = subprocess.run(cmd, capture_output=True, text=True, **kw)
    if r.returncode != 0:
        print(r.stdout[-2000:], file=sys.stderr)
        print(r.stderr[-2000:], file=sys.stderr)
        raise SystemExit(f"command failed ({r.returncode}): {cmd[0]} {cmd[1]}")
    return r.stdout


def write_script(theme):
    prompt = (
        "Write a 4-panel comic script about: " + theme + ". "
        'Return only JSON: {"title": "...", "panels": '
        '[{"image_prompt": "...", "caption": "..."}, x4]}. '
        "Keep the same characters, setting and art style in all four "
        "image_prompts. Captions are one short line each, in English."
    )
    out = run([
        "polli", "gen", "text", "--model", TEXT_MODEL,
        "--json-response", "--max-tokens", "600", prompt,
    ])
    data = json.loads(out)
    if "panels" not in data or len(data["panels"]) != 4:
        raise SystemExit(f"text model did not return 4 panels: {out[:300]}")
    return data


def draw_panel(image_prompt, path, seed):
    run([
        "polli", "gen", "image", "--model", IMAGE_MODEL,
        "--width", str(PANEL_W), "--height", str(PANEL_H),
        "--seed", str(seed), "--output", path,
        image_prompt + ", flat comic style, bold outlines",
    ])


def compose(panels, captions, title, out_path, font_path):
    from PIL import Image, ImageDraw, ImageFont

    try:
        font = ImageFont.truetype(font_path, 30) if font_path else ImageFont.load_default()
        title_font = ImageFont.truetype(font_path, 40) if font_path else ImageFont.load_default()
    except Exception:
        font = ImageFont.load_default()
        title_font = font
    cell_h = PANEL_H + CAPTION_H
    w = PANEL_W * 2 + GAP * 3
    h = 70 + (cell_h + GAP) * 2 + GAP
    strip = Image.new("RGB", (w, h), "white")
    d = ImageDraw.Draw(strip)
    d.text((GAP, 18), title, fill="black", font=title_font)
    for i, (panel_path, caption) in enumerate(zip(panels, captions)):
        img = Image.open(panel_path).convert("RGB").resize((PANEL_W, PANEL_H))
        x = GAP + (i % 2) * (PANEL_W + GAP)
        y = 70 + (i // 2) * (cell_h + GAP)
        strip.paste(img, (x, y))
        d.rectangle([x, y + PANEL_H, x + PANEL_W, y + cell_h], fill=(245, 245, 240))
        d.text((x + 10, y + PANEL_H + 16), caption[:60], fill="black", font=font)
    strip.save(out_path)
    print("wrote", out_path, strip.size)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--theme", default="a cat astronaut who is afraid of heights")
    ap.add_argument("--out", default="./comic-out")
    ap.add_argument("--script")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--font", default="")
    args = ap.parse_args()

    os.makedirs(args.out, exist_ok=True)
    if args.script:
        with open(args.script, encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = write_script(args.theme)
        with open(os.path.join(args.out, "panels.json"), "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    panels = []
    captions = []
    for i, p in enumerate(data["panels"]):
        path = os.path.join(args.out, f"panel{i + 1}.png")
        if not os.path.exists(path):
            draw_panel(p["image_prompt"], path, args.seed + i)
        panels.append(path)
        captions.append(p["caption"])
    compose(panels, captions, data.get("title", args.theme),
            os.path.join(args.out, "strip.png"), args.font)
    print("done:", os.path.join(args.out, "strip.png"))


if __name__ == "__main__":
    main()
