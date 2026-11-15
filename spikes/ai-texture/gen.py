"""Step 3 (AI texture spike): paint the 4 guide views in one 2x2 SDXL generation (consistent style across views).
img2img from our auto paint + depth ControlNet + IP-Adapter style reference (style blocks only).
.venv/bin/python gen.py <tag> [--strength 0.6] [--cn 0.6] [--ip 0.8] [--seed 1] [--steps 30]
Writes runs/<tag>/grid_in.png, grid_depth.png, grid_out.png and sheet.png + reference.json (for projection)."""
import argparse, json, time
from pathlib import Path

import numpy as np
import torch
from PIL import Image

HERE = Path(__file__).parent
G = HERE / "guides"
VIEWS = ["front", "side", "back", "side_mirror"]
S, CZ, EXT = 512, 1.08, 0.75
BG = (232, 232, 232)
PROMPT = ("hand-painted stylized game art, chibi skeleton knight head, dented purple painted iron helmet, "
          "thick orange-gold trim with round gold rivets, rust and scratches, bone skull with glowing blue eyes "
          "and big grinning teeth, strong light from top left, dark shadows, bold painterly brush strokes, "
          "mobile game asset, plain light grey background")
NEG = "photo, realistic, 3d render, plastic, blurry, noisy, text, watermark, frame, extra objects, people"

ap = argparse.ArgumentParser()
ap.add_argument("tag")
ap.add_argument("--strength", type=float, default=0.6)
ap.add_argument("--cn", type=float, default=0.6)
ap.add_argument("--ip", type=float, default=0.8)
ap.add_argument("--seed", type=int, default=1)
ap.add_argument("--steps", type=int, default=30)
ap.add_argument("--style", default=str(HERE / "style_ref.png"))
a = ap.parse_args()
out = HERE / "runs" / a.tag
out.mkdir(parents=True, exist_ok=True)

def grid(prefix, mode="RGB"):
    g = Image.new(mode, (2 * S, 2 * S))
    for i, v in enumerate(VIEWS):
        g.paste(Image.open(G / f"{prefix}_{v}.png").convert(mode), ((i % 2) * S, (i // 2) * S))
    return g

init, depth, mask = grid("init"), grid("depth"), grid("mask", "L")
init.save(out / "grid_in.png")
depth.save(out / "grid_depth.png")

from diffusers import AutoencoderKL, ControlNetModel, StableDiffusionXLControlNetImg2ImgPipeline
from transformers import CLIPVisionModelWithProjection

dt, dev = torch.float16, "mps"
t0 = time.time()
cn = ControlNetModel.from_pretrained("diffusers/controlnet-depth-sdxl-1.0", variant="fp16", torch_dtype=dt)
vae = AutoencoderKL.from_pretrained("madebyollin/sdxl-vae-fp16-fix", torch_dtype=dt)
enc = CLIPVisionModelWithProjection.from_pretrained("h94/IP-Adapter", subfolder="models/image_encoder", torch_dtype=dt)
pipe = StableDiffusionXLControlNetImg2ImgPipeline.from_pretrained(
    "stabilityai/stable-diffusion-xl-base-1.0", controlnet=cn, vae=vae, image_encoder=enc,
    variant="fp16", use_safetensors=True, torch_dtype=dt)
pipe.load_ip_adapter("h94/IP-Adapter", subfolder="sdxl_models", weight_name="ip-adapter-plus_sdxl_vit-h.safetensors")
pipe.set_ip_adapter_scale({"up": {"block_0": [0.0, a.ip, 0.0]}})   # InstantStyle: style block only
import gc
style = Image.open(a.style).convert("RGB")
# 16 GB machine: encode prompt and style image first, then drop those encoders before the UNet goes to the GPU
with torch.no_grad():
    for m in (pipe.text_encoder, pipe.text_encoder_2):
        m.to(dev)
    pe, npe, ppe, nppe = pipe.encode_prompt(PROMPT, device=dev, num_images_per_prompt=1,
                                            do_classifier_free_guidance=True, negative_prompt=NEG)
    pipe.text_encoder = pipe.text_encoder_2 = None
    gc.collect(); torch.mps.empty_cache()
    pipe.image_encoder.to(dev)
    ipe = pipe.prepare_ip_adapter_image_embeds(style, None, dev, 1, True)
    pipe.image_encoder = None
    gc.collect(); torch.mps.empty_cache()
for m in (pipe.unet, pipe.controlnet, pipe.vae):
    m.to(dev)
    gc.collect()
pipe.vae.enable_tiling()
print("loaded", round(time.time() - t0), "s", flush=True)
t0 = time.time()
img = pipe(prompt_embeds=pe, negative_prompt_embeds=npe, pooled_prompt_embeds=ppe,
           negative_pooled_prompt_embeds=nppe, ip_adapter_image_embeds=ipe,
           image=init, control_image=depth,
           strength=a.strength, controlnet_conditioning_scale=a.cn, num_inference_steps=a.steps,
           guidance_scale=6.0, generator=torch.Generator("cpu").manual_seed(a.seed),
           width=2 * S, height=2 * S).images[0]
print("generated", round(time.time() - t0), "s", flush=True)
img.save(out / "grid_out.png")

# projection sheet: [front | side | back | side_mirror flipped], background outside the silhouette
gen, m = np.array(img), np.array(mask) > 127
sheet = np.zeros((S, 4 * S, 3), dtype=np.uint8)
for i, v in enumerate(VIEWS):
    x, y = (i % 2) * S, (i // 2) * S
    cell = np.where(m[y:y + S, x:x + S, None], gen[y:y + S, x:x + S], np.array(BG, dtype=np.uint8))
    if v == "side_mirror":
        cell = cell[:, ::-1]
    sheet[:, i * S:(i + 1) * S] = cell
Image.fromarray(sheet).save(out / "sheet.png")
mpp = EXT / S
ref = {"m_per_px": mpp, "floor_y": S / 2 + CZ / mpp, "background": [c / 255 for c in BG],
       "views": {v: {"center_x": S / 2 + i * S, "x_range": [i * S, (i + 1) * S]} for i, v in enumerate(VIEWS)}}
(out / "reference.json").write_text(json.dumps(ref, indent=1))
json.dump(vars(a), open(out / "params.json", "w"), indent=1)
print("OK", out)
