"""Step 3 (AI texture spike): paint the 4 guide views in one 2x2 SDXL generation (consistent style across views).
img2img from our auto paint + depth ControlNet + IP-Adapter style reference (style blocks only).
.venv/bin/python gen.py <tag> [--strength 0.6] [--cn 0.6] [--ip 0.8] [--seed 1] [--steps 30] [--lightning 8] [--cfg 6]
    [--init-blur 0] [--depth-blur 0]   (px, masked Gaussian: hides the mesh facets the model reads as panels)
Writes runs/<tag>/grid_in.png, grid_depth.png, grid_out.png and sheet.png + reference.json (for projection)."""
import argparse, json, time
from pathlib import Path

import numpy as np
import torch
from PIL import Image, ImageFilter

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
ap.add_argument("--steps", type=int, default=None, help="default 30, or N with --lightning N")
ap.add_argument("--lightning", type=int, default=0, choices=[0, 2, 4, 8],
                help="SDXL-Lightning N-step LoRA (ByteDance, OpenRAIL++): Euler trailing, no CFG")
ap.add_argument("--cfg", type=float, default=None, help="guidance scale (default 6.0, or 1.0 = off with --lightning)")
ap.add_argument("--helmet", default="dented purple painted iron helmet",
                help="helmet words in the prompt (e.g. 'smooth one-piece dome')")
ap.add_argument("--neg-extra", default="", help="appended to the negative prompt")
ap.add_argument("--guides", default=str(HERE / "guides"), help="guide folder (guides.py output)")
ap.add_argument("--init-blur", type=float, default=0.0)
ap.add_argument("--depth-blur", type=float, default=0.0)
ap.add_argument("--style", default=str(HERE / "style_ref.png"))
a = ap.parse_args()
G = Path(a.guides)
a.steps = a.steps or (a.lightning or 30)
a.cfg = a.cfg if a.cfg is not None else (1.0 if a.lightning else 6.0)
CFG = a.cfg > 1.0
PROMPT = PROMPT.replace("dented purple painted iron helmet", a.helmet)
NEG = NEG + (", " + a.neg_extra if a.neg_extra else "")
out = HERE / "runs" / a.tag
out.mkdir(parents=True, exist_ok=True)

def grid(prefix, mode="RGB"):
    g = Image.new(mode, (2 * S, 2 * S))
    for i, v in enumerate(VIEWS):
        g.paste(Image.open(G / f"{prefix}_{v}.png").convert(mode), ((i % 2) * S, (i // 2) * S))
    return g

def masked_blur(img, mask, r):
    """Gaussian blur inside the silhouette only (normalised, so the background doesn't bleed in)."""
    if r <= 0:
        return img
    f = ImageFilter.GaussianBlur(r)
    blur = lambda x: np.asarray(Image.fromarray(np.clip(x, 0, 255).astype(np.uint8)).filter(f), dtype=np.float32)
    a = np.asarray(img, dtype=np.float32)
    m = np.asarray(mask, dtype=np.float32)[..., None] / 255
    num = np.dstack([blur(c) for c in np.moveaxis(a * m, -1, 0)])
    den = blur(m[..., 0] * 255)[..., None] / 255
    b = np.where(m > 0.5, num / np.maximum(den, 1e-4), a)
    return Image.fromarray(np.clip(b, 0, 255).astype(np.uint8))

init, depth, mask = grid("init"), grid("depth"), grid("mask", "L")
init = masked_blur(init, mask, a.init_blur)
depth = masked_blur(depth, mask, a.depth_blur)
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
if a.lightning:
    from diffusers import EulerDiscreteScheduler
    from huggingface_hub import hf_hub_download
    pipe.load_lora_weights(hf_hub_download("ByteDance/SDXL-Lightning", f"sdxl_lightning_{a.lightning}step_lora.safetensors"),
                           adapter_name="lightning")
    pipe.fuse_lora()
    pipe.scheduler = EulerDiscreteScheduler.from_config(pipe.scheduler.config, timestep_spacing="trailing")
pipe.set_ip_adapter_scale({"up": {"block_0": [0.0, a.ip, 0.0]}})   # InstantStyle: style block only
import gc
style = Image.open(a.style).convert("RGB")
# 16 GB machine: encode prompt and style image first, then drop those encoders before the UNet goes to the GPU
with torch.no_grad():
    for m in (pipe.text_encoder, pipe.text_encoder_2):
        m.to(dev)
    pe, npe, ppe, nppe = pipe.encode_prompt(PROMPT, device=dev, num_images_per_prompt=1,
                                            do_classifier_free_guidance=CFG, negative_prompt=NEG if CFG else None)
    pipe.text_encoder = pipe.text_encoder_2 = None
    gc.collect(); torch.mps.empty_cache()
    pipe.image_encoder.to(dev)
    ipe = pipe.prepare_ip_adapter_image_embeds(style, None, dev, 1, CFG)
    pipe.image_encoder = None
    gc.collect(); torch.mps.empty_cache()
for m in (pipe.unet, pipe.controlnet, pipe.vae):
    m.to(dev)
    gc.collect()
pipe.vae.enable_tiling()
print("loaded", round(time.time() - t0), "s", flush=True)
t0 = time.time()
neg = dict(negative_prompt_embeds=npe, negative_pooled_prompt_embeds=nppe) if CFG else {}
img = pipe(prompt_embeds=pe, pooled_prompt_embeds=ppe, ip_adapter_image_embeds=ipe, **neg,
           image=init, control_image=depth,
           strength=a.strength, controlnet_conditioning_scale=a.cn, num_inference_steps=a.steps,
           guidance_scale=a.cfg, generator=torch.Generator("cpu").manual_seed(a.seed),
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
