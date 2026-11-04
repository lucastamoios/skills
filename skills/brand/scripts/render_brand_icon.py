#!/usr/bin/env python3
"""Render an existing brand asset onto a transparent square PNG canvas.

Uses only the Python standard library plus macOS `qlmanage` and `sips`.
The source artwork is embedded without modification in an SVG wrapper, then
rendered at the requested size. This intentionally does not trim internal
padding from the source; callers should visually inspect the result.
"""

from __future__ import annotations

import argparse
import base64
import mimetypes
import pathlib
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET


RASTER_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp"}
SUPPORTED_SUFFIXES = RASTER_SUFFIXES | {".svg"}


def run(*args: str) -> str:
    result = subprocess.run(
        args,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    return result.stdout


def parse_number(value: str | None) -> float | None:
    if not value:
        return None
    cleaned = value.strip().lower()
    for unit in ("px", "pt", "pc", "mm", "cm", "in"):
        if cleaned.endswith(unit):
            cleaned = cleaned[: -len(unit)]
            break
    try:
        return float(cleaned)
    except ValueError:
        return None


def svg_dimensions(path: pathlib.Path) -> tuple[float, float]:
    root = ET.parse(path).getroot()
    view_box = root.get("viewBox") or root.get("viewbox")
    if view_box:
        parts = view_box.replace(",", " ").split()
        if len(parts) == 4:
            width, height = float(parts[2]), float(parts[3])
            if width > 0 and height > 0:
                return width, height
    width = parse_number(root.get("width"))
    height = parse_number(root.get("height"))
    if width and height and width > 0 and height > 0:
        return width, height
    raise ValueError("SVG needs a positive viewBox or numeric width and height")


def raster_dimensions(path: pathlib.Path) -> tuple[float, float]:
    output = run("sips", "-g", "pixelWidth", "-g", "pixelHeight", str(path))
    values: dict[str, float] = {}
    for line in output.splitlines():
        if ":" not in line:
            continue
        key, value = line.strip().split(":", 1)
        if key in {"pixelWidth", "pixelHeight"}:
            values[key] = float(value.strip())
    if values.get("pixelWidth", 0) <= 0 or values.get("pixelHeight", 0) <= 0:
        raise ValueError("Could not read raster dimensions with sips")
    return values["pixelWidth"], values["pixelHeight"]


def data_uri(path: pathlib.Path) -> str:
    mime = "image/svg+xml" if path.suffix.lower() == ".svg" else mimetypes.guess_type(path.name)[0]
    if not mime:
        raise ValueError(f"Could not determine MIME type for {path.name}")
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{encoded}"


def wrapper_svg(source: pathlib.Path, size: int, coverage: float) -> str:
    if source.suffix.lower() == ".svg":
        source_width, source_height = svg_dimensions(source)
    else:
        source_width, source_height = raster_dimensions(source)

    maximum = size * coverage
    scale = min(maximum / source_width, maximum / source_height)
    width = source_width * scale
    height = source_height * scale
    x = (size - width) / 2
    y = (size - height) / 2

    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" '
        f'viewBox="0 0 {size} {size}">\n'
        f'  <image href="{data_uri(source)}" x="{x:.6f}" y="{y:.6f}" '
        f'width="{width:.6f}" height="{height:.6f}" preserveAspectRatio="xMidYMid meet"/>\n'
        '</svg>\n'
    )


def sips_properties(path: pathlib.Path) -> dict[str, str]:
    output = run("sips", "-g", "pixelWidth", "-g", "pixelHeight", "-g", "hasAlpha", str(path))
    properties: dict[str, str] = {}
    for line in output.splitlines():
        if ":" in line:
            key, value = line.strip().split(":", 1)
            properties[key] = value.strip()
    return properties


def render(source: pathlib.Path, output: pathlib.Path, size: int, coverage: float) -> None:
    with tempfile.TemporaryDirectory(prefix="brand-icon-") as temporary:
        temporary_path = pathlib.Path(temporary)
        wrapper = temporary_path / "brand-wrapper.svg"
        rendered_directory = temporary_path / "rendered"
        rendered_directory.mkdir()
        wrapper.write_text(wrapper_svg(source, size, coverage), encoding="utf-8")

        run("qlmanage", "-t", "-s", str(size), "-o", str(rendered_directory), str(wrapper))
        rendered = rendered_directory / "brand-wrapper.svg.png"
        if not rendered.exists():
            candidates = list(rendered_directory.glob("*.png"))
            if len(candidates) != 1:
                raise RuntimeError("Quick Look did not produce exactly one PNG")
            rendered = candidates[0]

        properties = sips_properties(rendered)
        if properties.get("pixelWidth") != str(size) or properties.get("pixelHeight") != str(size):
            raise RuntimeError(f"Rendered dimensions are not {size} x {size}: {properties}")
        if properties.get("hasAlpha", "").lower() != "yes":
            raise RuntimeError("Rendered PNG does not have an alpha channel")

        output.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(rendered, output)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=pathlib.Path)
    parser.add_argument("output", type=pathlib.Path)
    parser.add_argument("--size", type=int, default=1254)
    parser.add_argument("--coverage", type=float, default=0.76)
    parser.add_argument("--force", action="store_true", help="allow replacing an existing output")
    args = parser.parse_args()

    source = args.source.expanduser().resolve()
    output = args.output.expanduser().resolve()
    if not source.is_file():
        parser.error(f"source does not exist: {source}")
    if source.suffix.lower() not in SUPPORTED_SUFFIXES:
        parser.error(f"unsupported source format: {source.suffix}")
    if args.size <= 0:
        parser.error("--size must be positive")
    if not 0 < args.coverage <= 1:
        parser.error("--coverage must be greater than 0 and at most 1")
    if output.suffix.lower() != ".png":
        parser.error("output must have a .png extension")
    if output.exists() and not args.force:
        parser.error(f"output exists; choose another filename or pass --force: {output}")
    if shutil.which("qlmanage") is None or shutil.which("sips") is None:
        parser.error("this helper requires macOS qlmanage and sips")

    try:
        render(source, output, args.size, args.coverage)
    except (OSError, ValueError, RuntimeError, subprocess.CalledProcessError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1

    properties = sips_properties(output)
    print(f"saved: {output}")
    print(f"dimensions: {properties.get('pixelWidth')} x {properties.get('pixelHeight')}")
    print(f"alpha: {properties.get('hasAlpha')}")
    print(f"coverage: {args.coverage:.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
