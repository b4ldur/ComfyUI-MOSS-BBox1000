# ComfyUI MOSS BBox 1000 Converter

A lightweight, dependency-free ComfyUI custom node that compiles **resolution-independent 0–1000 bounding boxes** into the **native centered pixel coordinates** used by [MOSS-Image](https://github.com/OpenMOSS/MOSS-Image#layout-to-image-generation).

This is a JSON coordinate **preprocessor**, not a feature built into MOSS-Image. It does not load image models, download weights, or access the network.

## Features

- Author layouts on a common `0–1000` top-left grid at any image resolution.
- Convert `relative_1000` → MOSS `abs_centralized` and preserve `yxyx` order.
- Set exact image width and height (multiples of 16) in the ComfyUI node.
- Preserve object descriptions, optional object tags, and literal text items.
- Validate input boxes; reject invalid values and accidental double conversion.
- Paste raw JSON or a Markdown response containing one layout JSON block.
- Python standard library only; no model dependencies added by this node.

## Installation

1. Clone the repository into `ComfyUI/custom_nodes/`:

   ```bash
   
cd /path/to/ComfyUI/custom_nodes
git clone https://github.com/b4ldur/ComfyUI-MOSS-BBox1000.git

   ```

   Replace `<account>` with the GitHub repository owner after publishing. Or download the repository as ZIP and extract it into `custom_nodes/ComfyUI-MOSS-BBox1000/`.
2. Restart the ComfyUI server.
3. Search for **MOSS BBox 1000 → Native** in category `MOSS-Image/layout`.

The node requires an existing MOSS-Image workflow and the matching model. No additional Python packages are required.

## Usage

1. Create a JSON layout using the format below, or copy [`examples/layout_1000.json`](examples/layout_1000.json).
2. Paste it into the node's `layout_json` field.
3. Set `width` and `height` to the **exact dimensions used by the generation latent** (not later resizing or upscaling).
4. Connect its `moss_native_json` STRING output to the `text` input of the positive text-encoding node in your MOSS-Image workflow. In ComfyUI, convert the text widget to an input if necessary.
5. Run your normal MOSS-Image workflow.

```text
0–1000 layout JSON
       |
       v
[MOSS BBox 1000 → Native] -- moss_native_json --> [positive text encoder] --> MOSS sampling
        width / height <------------------------------ generation image size
```

The input layout is **not** native MOSS JSON; the output is. Do not pass the `relative_1000` layout directly to the model.

## Coordinate contract

The universal grid uses top-left origin with x right and y down. Boxes use `[top, left, bottom, right]` integers inclusive of grid limits `0–1000`; `top < bottom`, `left < right`.

- Authoring marker: `"bbox_coord_space": "relative_1000"` (custom, not recognized natively by MOSS).
- Native output marker: `"bbox_coord_space": "abs_centralized"`.
- Both formats: `"bbox_format": "yxyx"`.
- `relative_1000` box `[0,0,1000,1000]` always maps to the complete output canvas.

A coordinate transforms as follows (with rounding to the nearest integer pixel):

```text
x_native = (x_grid / 1000 - 0.5) * width
y_native = (y_grid / 1000 - 0.5) * height
```

| Region | Grid box | Native box at 1248 × 1680 |
|---|---|---|
| Full image | `[0, 0, 1000, 1000]` | `[-840, -624, 840, 624]` |
| Central region | `[150, 200, 850, 800]` | `[-588, -374, 588, 374]` |

**Aspect-ratio note:** X and Y scale separately. A box that is square in the 0–1000 grid is only pixel-square when width equals height. For rigid geometry, adapt the source boxes to the intended canvas or use other geometry constraints.

## Minimal JSON input

```json
{
  "summary": {
    "meta": ["graphic design"],
    "canvas": "single",
    "caption": "A clean full-bleed poster with one central object."
  },
  "items": [
    {
      "label": "object",
      "caption": "Background filling the canvas.",
      "bbox": [0, 0, 1000, 1000]
    },
    {
      "label": "object",
      "caption": "A geometric shape in the center.",
      "bbox": [300, 300, 700, 700]
    }
  ],
  "bbox_coord_space": "relative_1000",
  "bbox_format": "yxyx"
}
```

The converter also supports `label: "text"` with a literal `text` field, for example the corner-label test in [`examples/layout_1000.json`](examples/layout_1000.json).

For generating valid authoring JSON with an LLM, use the neutral template at [`prompts/SYSTEM_PROMPT.md`](prompts/SYSTEM_PROMPT.md).

## Standalone command line

```bash
python tools/convert.py examples/layout_1000.json --width 1248 --height 1680 -o output_native.json
```

## Tests

```bash
python -m unittest discover -s tests -v
```

Automated GitHub Actions tests cover multiple image sizes and invalid coordinates. The converter itself has been tested without ComfyUI; the full MOSS image-generation workflow still needs an environment with ComfyUI and MOSS-Image installed.

## Limitations

- The coordinate conversion is deterministic; image-model adherence to precise boxes is approximate.
- A layout intended for one aspect ratio may need artistic reframing on another.
- The converter extracts **the first** layout JSON object if multiple objects are pasted; process different layouts separately.
- Width and height must be 16–16384 pixels and multiples of 16.
- Not affiliated with or an official component of OpenMOSS or ComfyUI.

## License

MIT — see [LICENSE](LICENSE).
