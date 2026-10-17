"""Convert virtual [0,1000] top-left yxyx boxes to native MOSS centered pixels.

Pure Python, no runtime dependencies beyond the standard library.
"""

import json
from typing import Any

_AUTHOR_MARKERS = {None, "relative_1000", "normalized_1000", "0_1000"}


def extract_layout(text: str) -> dict[str, Any]:
    """Find the first valid layout JSON object in raw JSON or markdown output.

    This lets users paste a system-prompt response with markdown headings and
    both JSON and natural-language modes directly into the ComfyUI node.
    """
    if not isinstance(text, str) or not text.strip():
        raise ValueError("Paste your 0–1000 layout JSON into the layout_json input.")

    decoder = json.JSONDecoder()
    for idx, char in enumerate(text):
        if char != "{":
            continue
        try:
            candidate, _ = decoder.raw_decode(text[idx:])
        except json.JSONDecodeError:
            continue
        if isinstance(candidate, dict) and "summary" in candidate and "items" in candidate:
            return candidate
    raise ValueError("Could not find a valid layout JSON object with summary and items. Check JSON syntax.")


def _integer_in_grid(value: Any, item_index: int, coordinate_name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"Item {item_index}: {coordinate_name} must be an integer, got {value!r}.")
    if not (0 <= value <= 1000):
        raise ValueError(f"Item {item_index}: {coordinate_name}={value} is outside [0, 1000].")
    return value


def _convert_axis(coord: int, dimension: int) -> int:
    # Uses integer arithmetic for deterministic nearest-integer conversion.
    # Width/height are multiples of 16 so full-image bounds remain exact.
    # Python round() does banker's rounding; use half-away-from-zero here
    # for predictable symmetric boxes at boundary coordinates.
    numerator = (coord * 2 - 1000) * dimension
    denominator = 2000
    return ((numerator + denominator // 2) // denominator
            if numerator >= 0 else -((-numerator + denominator // 2) // denominator))


def convert_layout(layout: dict[str, Any], width: int, height: int) -> dict[str, Any]:
    """Validate a normalized draft and construct strict native MOSS layout.

    The authored schema uses top-left 0–1000 coordinates; output uses native
    abs_centralized yxyx coordinates. No in-place mutation of input layout.
    """
    if any(isinstance(d, bool) or not isinstance(d, int) for d in (width, height)):
        raise ValueError("width and height must be integer pixel dimensions.")
    if not (16 <= width <= 16384 and 16 <= height <= 16384):
        raise ValueError("width and height must each be between 16 and 16384.")
    if width % 16 or height % 16:
        raise ValueError("width and height must be multiples of 16.")
    if not isinstance(layout, dict):
        raise ValueError("Layout must be a JSON object.")

    coord_space = layout.get("bbox_coord_space")
    if coord_space == "abs_centralized":
        raise ValueError("Input is already native abs_centralized. Do not convert it again.")
    if coord_space not in _AUTHOR_MARKERS:
        raise ValueError(f"Unsupported input bbox_coord_space: {coord_space!r}. Expected relative_1000.")
    if layout.get("bbox_format", "yxyx") != "yxyx":
        raise ValueError('Input bbox_format must be "yxyx" (top, left, bottom, right).')

    summary = layout.get("summary")
    if not isinstance(summary, dict):
        raise ValueError('Layout must contain a "summary" object.')
    meta = summary.get("meta")
    caption = summary.get("caption")
    if not isinstance(meta, list) or not (1 <= len(meta) <= 4) or not all(isinstance(x, str) for x in meta):
        raise ValueError("summary.meta must be an array of 1–4 style strings.")
    if not isinstance(caption, str) or not caption.strip():
        raise ValueError("summary.caption must be a non-empty string.")
    if summary.get("canvas") != "single":
        raise ValueError('summary.canvas must equal "single".')
    items = layout.get("items")
    if not isinstance(items, list) or not items:
        raise ValueError('Layout must contain a non-empty "items" array.')

    result = {
        "summary": {"meta": meta, "canvas": "single", "caption": caption},
        "items": [],
        "bbox_coord_space": "abs_centralized",
        "bbox_format": "yxyx",
    }

    for i, item in enumerate(items):
        if not isinstance(item, dict):
            raise ValueError(f"Item {i}: expected an object.")
        label = item.get("label")
        if label not in {"object", "text"}:
            raise ValueError(f"Item {i}: label must be 'object' or 'text'.")
        item_caption = item.get("caption")
        if not isinstance(item_caption, str) or not item_caption.strip():
            raise ValueError(f"Item {i}: caption must be non-empty text.")
        bbox = item.get("bbox")
        if not isinstance(bbox, list) or len(bbox) != 4:
            raise ValueError(f"Item {i}: bbox must be [top, left, bottom, right].")

        names = ("top", "left", "bottom", "right")
        top, left, bottom, right = (
            _integer_in_grid(value, i, name) for value, name in zip(bbox, names)
        )
        if not (top < bottom and left < right):
            raise ValueError(f"Item {i}: bbox needs top < bottom and left < right.")
        converted_box = [
            _convert_axis(top, height),
            _convert_axis(left, width),
            _convert_axis(bottom, height),
            _convert_axis(right, width),
        ]
        if not (converted_box[0] < converted_box[2] and converted_box[1] < converted_box[3]):
            raise ValueError(f"Item {i}: box became zero-area at {width}×{height}; enlarge it in the 0–1000 grid.")

        converted = {"label": label, "caption": item_caption}
        if label == "text":
            literal = item.get("text")
            if not isinstance(literal, str) or not literal:
                raise ValueError(f"Item {i}: text item requires an exact non-empty text value.")
            converted["text"] = literal
        else:
            if "text" in item:
                raise ValueError(f"Item {i}: object items must not contain 'text'.")
            if "tags" in item:
                tags = item["tags"]
                if not isinstance(tags, list) or not all(isinstance(tag, str) for tag in tags):
                    raise ValueError(f"Item {i}: tags must be an array of strings.")
                converted["tags"] = tags
        converted["bbox"] = converted_box
        result["items"].append(converted)

    return result


def convert_text(text: str, width: int, height: int, pretty: bool = False) -> str:
    layout = extract_layout(text)
    native = convert_layout(layout, width, height)
    if pretty:
        return json.dumps(native, ensure_ascii=False, indent=2)
    return json.dumps(native, ensure_ascii=False, separators=(",", ":"))
