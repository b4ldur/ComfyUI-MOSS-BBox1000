# MOSS-Image 0–1000 Grid Layout Prompt

Generate one **valid JSON layout** for MOSS-Image. Output only a `json` code block, without explanations. Use the virtual 0–1000 authoring grid; **do not output native pixel coordinates**.

## Coordinate rules

- Origin `(0,0)` is top-left. X increases right; Y increases down.
- Both axes run from 0 to 1000, independently of image resolution and aspect ratio.
- Boxes use **`[y_min, x_min, y_max, x_max]`** (top, left, bottom, right).
- Coordinates are integers in `[0,1000]`; `y_min < y_max` and `x_min < x_max`.
- Use exactly `"bbox_coord_space": "relative_1000"` and `"bbox_format": "yxyx"`.
- `relative_1000` is a custom authoring format. A converter must translate it to MOSS's native `abs_centralized` coordinates before image generation.

## Layout rules

- Assign one `items` entry to each distinct object or text region.
- Use `label: "object"` for objects, `label: "text"` with exact `text` for written words.
- Captions describe appearance and intended position, consistent with the box.
- Respect specified margins: an object in a corner need not touch the canvas edge.
- For a full-bleed background, use `[0,0,1000,1000]`.
- Use boxes suitable for the user's composition. Avoid accidental overlap or clipping.
- Independent X/Y scaling preserves normalized placement, **not** necessarily circles, squares, or physical proportions on different aspect ratios.
- Do not add width or height keys. Generate separate JSON objects for separate concepts.

## Required format

```json
{
  "summary": {
    "meta": ["graphic design"],
    "canvas": "single",
    "caption": "Overall scene description."
  },
  "items": [
    {
      "label": "object",
      "caption": "Full-frame background.",
      "bbox": [0, 0, 1000, 1000]
    },
    {
      "label": "text",
      "caption": "Title near the top, inset from the sides.",
      "text": "TITLE",
      "bbox": [50, 200, 150, 800]
    }
  ],
  "bbox_coord_space": "relative_1000",
  "bbox_format": "yxyx"
}
```

Before replying, verify JSON syntax, schema fields, box order, integer bounds, and placement.
