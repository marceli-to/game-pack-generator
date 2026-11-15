# Spike: AI-painted textures (local SDXL)

Can an image model paint our meshes in the style of Marcel's sheets? Geometry, UVs, rig and export stay ours;
only the texture comes from the model. Result on the v3 knight head (2026-11-15): clearly better than `auto`
paint (face, gold, damage), but ~18 min per image on a 16 GB M1 Pro (swapping). Next: run on the Mac Studio.

## How it works

1. `knight_v3.py`: assemble the test knight (head only: `head-skull-grin` + `headwear-helmet-bell`) and paint it
   with `auto` (start image for the model).
2. `guides.py` (Blender): per view (front, side, back, side_mirror; 512 px) the auto-paint render (`init_*`),
   a depth map (`depth_*`, near = white) and a silhouette mask (`mask_*`).
3. `gen.py`: the 4 views as one 2×2 image (1024²) in one SDXL pass, so all views share one style:
   img2img from the auto paint + depth ControlNet + IP-Adapter style reference (`style_ref.png`, crop of the knight
   sheet; style blocks only, "InstantStyle"). Writes a projection sheet + `reference.json`.
4. `project.py`: our `projection` paint (z-buffer + facing weights, auto paint where no view sees) bakes the views
   onto the mesh; `compare.png` = reference / auto / AI.

Models (Hugging Face, ~13 GB, cached in `~/.cache/huggingface`): `stabilityai/stable-diffusion-xl-base-1.0`
(CreativeML Open RAIL++-M), `diffusers/controlnet-depth-sdxl-1.0` (OpenRAIL++), `madebyollin/sdxl-vae-fp16-fix`
(MIT), `h94/IP-Adapter` (Apache 2.0). All allow commercial use of the outputs (packs are CC0).

## Setup (once per machine)

The main repo set-up first (README: `.venv`, Blender 5.2.4, `library/`), then:

```sh
cd spikes/ai-texture
/opt/homebrew/bin/python3.13 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

## Run (from the repo root)

```sh
.venv/bin/python spikes/ai-texture/knight_v3.py                                   # ~20 s
/Applications/Blender.app/Contents/MacOS/Blender -b workspace/knight-v3/character.blend \
  --factory-startup -P spikes/ai-texture/guides.py -- spikes/ai-texture/guides .  # ~10 s
spikes/ai-texture/.venv/bin/python spikes/ai-texture/gen.py a1                    # first run downloads the models
.venv/bin/python spikes/ai-texture/project.py a1                                  # -> runs/a1/compare.png
```

`gen.py` options: `--strength` (img2img, 0.6), `--cn` (depth ControlNet weight, 0.6), `--ip` (style weight, 0.8),
`--seed`, `--steps` (30; img2img runs strength × steps). It encodes prompt and style image first and frees those
encoders before the UNet goes to the GPU (needed at 16 GB; harmless with more RAM).

## Known issues / next

- Vertical "plank" lines on the dome: the model reads the 16 flat dome segments (visible in the faceted auto-paint
  start image) as panels → smooth the start image / depth, or lower `--cn`.
- Iron still lighter and more even than the sheet.
- Speed: try a few-step SDXL variant (SDXL-Lightning, 4–8 steps) and the Studio's RAM/GPU.
- If it holds up: an `ai` approach in `paint_surface` (guides → generation → projection in one call).
