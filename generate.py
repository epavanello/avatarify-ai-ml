import os
import random
import torch
from torch import autocast
from diffusers import StableDiffusionPipeline, DDIMScheduler
from supabase import create_client, Client
import config
from typing import Optional

Root = os.getcwd()


def generate(session_name: str, theme: str, prompt: str, seed: Optional[int]):
    MODEL_DIR = os.path.join(Root, "models", session_name)

    conf = config.Settings()
    supabase: Client = create_client(conf.supabase_url, conf.supabase_key)

    OUTPUT_DIR = os.path.join(Root, "sessions", session_name, "output")

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    # If you want to use previously trained model saved in gdrive, replace this with the full path of model in gdrive
    session_ckpt_link_path = os.path.join(
        Root, "sessions", session_name, session_name + ".ckpt")
    if not os.path.exists(session_ckpt_link_path):
        os.symlink(os.path.join(MODEL_DIR, session_name + ".ckpt"),
                   session_ckpt_link_path)
    model_path = MODEL_DIR

    scheduler = DDIMScheduler(beta_start=0.00085, beta_end=0.012,
                              beta_schedule="scaled_linear", clip_sample=False, set_alpha_to_one=False)
    pipe = StableDiffusionPipeline.from_pretrained(
        model_path, scheduler=scheduler, safety_checker=None, torch_dtype=torch.float16).to("cuda")

    g_cuda = None

    # @markdown Can set random seed here for reproducibility.
    g_cuda = torch.Generator(device='cuda')
    seed = seed or random.randint(1, 999999)  # @param {type:"number"}
    g_cuda.manual_seed(seed)

    # @title Run for generating images.

    prompt = prompt  # f"ejxjo"  # @param {type:"string"}
    negative_prompt = "(disfigured), (bad art), (deformed), (poorly drawn), (extra limbs), strange colours, blurry, boring, sketch, lacklustre, repetitive, cropped, hands"  # @param {type:"string"}
    num_samples = 1  # @param {type:"number"}
    guidance_scale = 7.5  # @param {type:"number"}
    num_inference_steps = 50  # @param {type:"number"}
    height = 512  # @param {type:"number"}
    width = 512  # @param {type:"number"}

    with autocast("cuda"), torch.inference_mode():
        images = pipe(
            prompt,
            height=height,
            width=width,
            negative_prompt=negative_prompt,
            num_images_per_prompt=num_samples,
            num_inference_steps=num_inference_steps,
            guidance_scale=guidance_scale,
            generator=g_cuda
        ).images

    photos_generated = supabase.storage().get_bucket(
        "photos-generated")

    start_index = len(photos_generated.list(session_name))

    for index, img in enumerate(images):
        # Do not use here path.join because under windows \ break the api
        # Add style name
        filename = theme + "_" + str(seed) + ".jpg"
        filepath_tmp = os.path.join(OUTPUT_DIR, filename)

        img.save(filepath_tmp)
        resp = photos_generated.upload(session_name + "/" + str(start_index + index + 1) + "_" + filename,
                                       filepath_tmp)
        os.remove(filepath_tmp)
        assert resp.is_success
