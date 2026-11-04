---
name: brand
description: Find canonical company, product, or personal-site marks and prepare them as transparent, consistently sized PNG icons for 1Password or similar icon collections. Use when the user asks to fetch, extract, normalize, or save an existing brand icon; do not use to invent or redesign a logo.
---

# Brand Icon

## Private configuration

For ordinary use, read the installed `skill-config` skill and resolve the profile fields below. Set `SKILL_CONFIG` to its `scripts/config.py` absolute path before shell examples. For a prepared worker packet, use only its supplied values and explicitly permitted private resources. Ask for required missing fields; do not load unrelated private context.

Prepare the canonical mark, not an approximation. Preserve the source artwork and make only the transformations required for canvas size, padding, format, and transparency.

## Establish the collection format

If the user points to an existing icon folder, inspect at least three representative icons before processing the new one. Infer canvas dimensions, apparent mark coverage, padding, color treatment, transparency, and filename conventions. Follow explicit user requirements over inferred conventions.

When the user gives no format, use a transparent 1254 x 1254 PNG with the mark centered and enough clear space to remain legible at 1Password sizes. The established default destination is `~/Pictures/1Password Icons/<Brand>.png` only when the user refers to that collection or asks to save it "there"; otherwise ask for or infer the destination from context.

## Choose the canonical source

Prefer sources in this order:

1. An asset or path supplied by the user.
2. A canonical asset in the user's project or local repository.
3. The brand's official kit, press page, documentation, or website metadata.
4. The brand's official source repository.
5. A third-party source only after disclosing that no canonical asset was found.

For a local project, search filenames and code references for `icon`, `apple-icon`, `favicon`, `logo`, manifests, and page metadata. If an expected private repository is absent locally but its identity can be established safely, inspect a temporary shallow clone and never modify that checkout.

For an online brand, browse the current official brand page. Download the official kit when available and retain the source URL for the final report.

Do not use image generation to reproduce an existing mark when a canonical vector or raster asset exists.

## Select the variant

- Prefer a symbol or logomark over a wordmark for square icon slots.
- Prefer SVG or the largest transparent raster source.
- Prefer the official flat or monochrome mark when the collection uses unstyled symbols.
- Preserve official geometry and colors.
- Do not stretch, crop, recolor, add shadows, add backgrounds, round corners, or combine graphics unless the user requests it or the official asset already includes that treatment.
- Avoid upscaling a tiny raster when a vector or larger canonical source exists. If no better source exists, preserve it and disclose the resolution limitation.

## Normalize and validate

Use the bundled `scripts/render_brand_icon.py` for ordinary SVG, PNG, JPEG, or WebP sources on macOS. Adjust `--coverage` to match the apparent scale of the inspected collection; the default is 0.76. The helper preserves aspect ratio, creates a transparent square canvas, centers the source, refuses to overwrite by default, and validates dimensions and alpha.

```bash
python3 "$(python3 "$SKILL_CONFIG" get paths.skills --path)/brand/scripts/render_brand_icon.py" SOURCE OUTPUT \
  --size 1254 \
  --coverage 0.76
```

If the selected source already contains substantial internal clear space, reduce added padding or prepare a temporary tightly bounded canonical variant before rendering. Do not alter the original asset.

Before saving, visually inspect the rendered result and verify:

- exact square dimensions;
- alpha channel and transparent outer canvas;
- no clipping, distortion, or unexpected background;
- balanced apparent padding relative to the comparison icons;
- correct official variant and color.

If the destination exists and the user did not explicitly request replacement, save a versioned sibling such as `<Brand>-v2.png`.

## Report the result

Return a clickable absolute path and a preview. State the source, selected variant, dimensions, transparency, and whether AI generation was avoided. Link the official source when one was used. Remove temporary downloads and extracted archives after the final artifact is verified.
