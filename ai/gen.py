"""AI texture generation for the `ai` painted approach (styles/painted STYLE.md §4). Runs in ai/.venv
(torch + diffusers), not in the server's venv:  ai/.venv/bin/python ai/gen.py <args.json> <result.json>

args: { guides_dir (ai_guides output), out_dir, prompt, negative, style_ref (image path), seed, steps,
        strength, controlnet, ip_adapter, guidance, view_size, background [r, g, b] (0-255),
        models: {base, controlnet, vae, ip_adapter: [repo, subfolder, file], image_encoder: [repo, subfolder]},
        lightning?: 0 | 2 | 4 | 8 (SDXL-Lightning LoRA; then steps/guidance as given) }
The 4 guide views go into one 2x2 image and one SDXL pass (one style across views): img2img from the
start image + depth ControlNet + IP-Adapter style reference (style blocks only, "InstantStyle").
Writes grid_in.png, grid_depth.png, grid_out.png, sheet.png ([front | side | back | side_mirror], the
mirror flipped to projection orientation, background outside the silhouette) and reference.json.
Result: { ok, outputs, stats: {load_s, gen_s, device}, error? }."""
import gc
import json
import shutil
import sys
import time
import traceback
from pathlib import Path

VIEWS = ["front", "side", "back", "side_mirror"]


def generate(a):
    import numpy as np
    import torch
    from diffusers import AutoencoderKL, ControlNetModel, StableDiffusionXLControlNetImg2ImgPipeline
    from PIL import Image
    from transformers import CLIPVisionModelWithProjection

    S, G, out = a["view_size"], Path(a["guides_dir"]), Path(a["out_dir"])
    out.mkdir(parents=True, exist_ok=True)

    def grid(prefix, mode="RGB"):
        g = Image.new(mode, (2 * S, 2 * S))
        for i, v in enumerate(VIEWS):
            g.paste(Image.open(G / f"{prefix}_{v}.png").convert(mode).resize((S, S)), ((i % 2) * S, (i // 2) * S))
        return g

    init, depth, mask = grid("init"), grid("depth"), grid("mask", "L")
    init.save(out / "grid_in.png")
    depth.save(out / "grid_depth.png")

    dev = "mps" if torch.backends.mps.is_available() else ("cuda" if torch.cuda.is_available() else "cpu")
    dt = torch.float16 if dev != "cpu" else torch.float32
    var = "fp16" if dt == torch.float16 else None
    m = a["models"]
    t0 = time.time()
    cn = ControlNetModel.from_pretrained(m["controlnet"], variant=var, torch_dtype=dt)
    vae = AutoencoderKL.from_pretrained(m["vae"], torch_dtype=dt)
    enc = CLIPVisionModelWithProjection.from_pretrained(m["image_encoder"][0], subfolder=m["image_encoder"][1],
                                                        torch_dtype=dt)
    pipe = StableDiffusionXLControlNetImg2ImgPipeline.from_pretrained(
        m["base"], controlnet=cn, vae=vae, image_encoder=enc, variant=var, use_safetensors=True, torch_dtype=dt)
    pipe.load_ip_adapter(m["ip_adapter"][0], subfolder=m["ip_adapter"][1], weight_name=m["ip_adapter"][2])
    if a.get("lightning"):
        from diffusers import EulerDiscreteScheduler
        from huggingface_hub import hf_hub_download
        pipe.load_lora_weights(hf_hub_download("ByteDance/SDXL-Lightning",
                                               f"sdxl_lightning_{a['lightning']}step_lora.safetensors"))
        pipe.fuse_lora()
        pipe.scheduler = EulerDiscreteScheduler.from_config(pipe.scheduler.config, timestep_spacing="trailing")
    pipe.set_ip_adapter_scale({"up": {"block_0": [0.0, a["ip_adapter"], 0.0]}})
    cfg_on = a["guidance"] > 1.0
    style = Image.open(a["style_ref"]).convert("RGB")
    # encode prompt and style image first, then free those encoders before the UNet goes to the GPU
    # (needed on 16 GB machines, harmless with more)
    with torch.no_grad():
        for enc_m in (pipe.text_encoder, pipe.text_encoder_2):
            enc_m.to(dev)
        pe, npe, ppe, nppe = pipe.encode_prompt(a["prompt"], device=dev, num_images_per_prompt=1,
                                                do_classifier_free_guidance=cfg_on,
                                                negative_prompt=a["negative"] if cfg_on else None)
        pipe.text_encoder = pipe.text_encoder_2 = None
        gc.collect()
        pipe.image_encoder.to(dev)
        ipe = pipe.prepare_ip_adapter_image_embeds(style, None, dev, 1, cfg_on)
        pipe.image_encoder = None
        gc.collect()
    for mod in (pipe.unet, pipe.controlnet, pipe.vae):
        mod.to(dev)
    pipe.vae.enable_tiling()
    load_s = time.time() - t0
    t0 = time.time()
    neg = dict(negative_prompt_embeds=npe, negative_pooled_prompt_embeds=nppe) if cfg_on else {}
    img = pipe(prompt_embeds=pe, pooled_prompt_embeds=ppe, ip_adapter_image_embeds=ipe, **neg,
               image=init, control_image=depth, strength=a["strength"],
               controlnet_conditioning_scale=a["controlnet"], num_inference_steps=a["steps"],
               guidance_scale=a["guidance"], generator=torch.Generator("cpu").manual_seed(a["seed"]),
               width=2 * S, height=2 * S).images[0]
    gen_s = time.time() - t0
    img.save(out / "grid_out.png")

    gen, msk = np.array(img), np.array(mask) > 127
    bg = np.array(a["background"], dtype=np.uint8)
    sheet = np.zeros((S, 4 * S, 3), dtype=np.uint8)
    for i, v in enumerate(VIEWS):
        x, y = (i % 2) * S, (i // 2) * S
        cell = np.where(msk[y:y + S, x:x + S, None], gen[y:y + S, x:x + S], bg)
        if v == "side_mirror":
            cell = cell[:, ::-1]
        sheet[:, i * S:(i + 1) * S] = cell
    Image.fromarray(sheet).save(out / "sheet.png")
    shutil.copy(G / "reference.json", out / "reference.json")
    files = [str(out / f) for f in ("grid_in.png", "grid_depth.png", "grid_out.png", "sheet.png", "reference.json")]
    return {"outputs": files, "stats": {"load_s": round(load_s, 1), "gen_s": round(gen_s, 1), "device": dev}}


def main():
    args_path, result_path = Path(sys.argv[1]), Path(sys.argv[2])
    result = {"ok": False, "outputs": [], "stats": {}}
    try:
        result.update(generate(json.loads(args_path.read_text())))
        result["ok"] = True
    except Exception as e:  # noqa: BLE001 - report everything back to the caller
        result["error"] = f"{type(e).__name__}: {e}"
        result["traceback"] = traceback.format_exc()
    result_path.write_text(json.dumps(result, indent=1))
    sys.exit(0 if result["ok"] else 1)


if __name__ == "__main__":
    main()
