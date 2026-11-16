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

`gen.py` options: `--guides` (folder), `--init-blur` / `--depth-blur` (px, masked), `--helmet` / `--neg-extra`
(prompt words), `--lightning N` / `--cfg` (few-step LoRA, needs `peft`), `--strength` (img2img, 0.6), `--cn` (depth ControlNet weight, 0.6), `--ip` (style weight, 0.8),
`--seed`, `--steps` (30; img2img runs strength × steps). It encodes prompt and style image first and frees those
encoders before the UNet goes to the GPU (needed at 16 GB; harmless with more RAM).

## Known issues / next

- ~~Plank lines on the dome~~ fixed (2026-11-16): the **depth ControlNet** read the 16 flat dome segments as panels
  (`--cn 0` → no planks; no style ref, smooth start image, blurred depth, lower `--cn` or prompt words → still
  planks). `guides.py` now renders depth from a subdivided copy (`GUIDE_SUBSURF`, default 2; edges over 40°
  creased, so only soft facets round off). Runs `f1`/`f2` (seeds 1/2): clean dome, detail kept.
- Iron still lighter and more even than the sheet.
- Speed (2026-11-16, M4 Max): full SDXL 27 s/image; **SDXL-Lightning** (`--lightning 8 --steps 13`, 7 steps run)
  6 s, `--cfg 2` 11 s. Lightning looks cleaner/flatter and stays closer to the start image (hole keeps the
  procedural star shape, less painterly damage); strength 0.75 / ip 1.1 / cfg 2 change little. Runs `g1`–`g6` vs `f1`.
- ~~An `ai` approach in `paint_surface`~~ done (2026-11-16): `paint_surface(name, approach="ai", subject=…)`,
  code in `ai/gen.py`, `jobs/ai_guides.py`, `server/ai.py`; settings in `styles/painted/style.json` `paint.ai`.
  This folder stays as the experiment bench (blur/prompt/Lightning knobs, comparison sheets).
