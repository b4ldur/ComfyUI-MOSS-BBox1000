# Public GitHub release checklist

- [ ] Review all repository files for names, accounts, local paths, credentials, private data, and unwanted content.
- [ ] Create a fresh GitHub repository named `ComfyUI-MOSS-BBox1000` (or another neutral name).
- [ ] Commit the contents of this directory **only**; do not include old ZIPs, user images, private prompts, or model weights.
- [ ] Run `python -m unittest discover -s tests -v` locally.
- [ ] Verify the workflow with a live MOSS-Image ComfyUI installation.
- [ ] Replace the sample `<account>` URL in README with the actual public repository URL.
- [ ] Decide whether to keep the provided MIT license and replace the generic `Contributors` copyright if attribution is desired.
- [ ] Create a public GitHub release/tag after testing (suggested starting tag: `v0.1.0`).
- [ ] Optional: Comfy Registry publishing requires separate publisher registration/metadata. GitHub publication alone does not register a node in Comfy Registry.

Suggested repository topics: `comfyui`, `custom-nodes`, `moss-image`, `bbox`, `layout`, `image-generation`.
