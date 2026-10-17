"""ComfyUI node for converting relative 0–1000 MOSS-Image layout boxes."""

from .core import convert_text


_DEFAULT_LAYOUT = '''{
  "summary": {
    "meta": ["minimal graphic design"],
    "canvas": "single",
    "caption": "A clean full-bleed poster with a centered geometric shape and a title."
  },
  "items": [
    {
      "label": "object",
      "caption": "A solid background filling the entire canvas.",
      "bbox": [0, 0, 1000, 1000]
    },
    {
      "label": "object",
      "caption": "A geometric shape in the center of the poster.",
      "bbox": [300, 300, 700, 700]
    },
    {
      "label": "text",
      "caption": "A short title near the top of the poster.",
      "text": "EXAMPLE",
      "bbox": [50, 250, 150, 750]
    }
  ],
  "bbox_coord_space": "relative_1000",
  "bbox_format": "yxyx"
}'''


class MossBBox1000ToNative:
    """Compile a resolution-independent authoring layout for MOSS-Image."""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "layout_json": ("STRING", {
                    "multiline": True,
                    "default": _DEFAULT_LAYOUT,
                    "dynamicPrompts": False,
                }),
                "width": ("INT", {"default": 1248, "min": 16, "max": 16384, "step": 16}),
                "height": ("INT", {"default": 1680, "min": 16, "max": 16384, "step": 16}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("moss_native_json",)
    FUNCTION = "compile_layout"
    CATEGORY = "MOSS-Image/layout"
    DESCRIPTION = (
        "Convert a relative 0–1000 yxyx layout to MOSS-Image native "
        "abs_centralized pixel coordinates at the specified dimensions."
    )

    def compile_layout(self, layout_json, width, height):
        try:
            output = convert_text(layout_json, width, height)
        except ValueError as exc:
            raise ValueError(f"MOSS BBox 1000: {exc}") from exc
        return (output,)


# Preserve the original class key for existing ComfyUI workflows.
NODE_CLASS_MAPPINGS = {"MossBBox1000ToNative": MossBBox1000ToNative}
NODE_DISPLAY_NAME_MAPPINGS = {"MossBBox1000ToNative": "MOSS BBox 1000 → Native"}
