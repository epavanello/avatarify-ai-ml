from glob import glob
import os
import random
import torch
from torch import autocast
from diffusers import StableDiffusionPipeline, DDIMScheduler

from natsort import natsorted
Root = os.getcwd()


def generate(session_name: str):
    MODEL_DIR = os.path.join(Root, "models", session_name)
    OUTPUT_DIR = os.path.join(Root, "sessions", session_name, "output")

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    # If you want to use previously trained model saved in gdrive, replace this with the full path of model in gdrive
    session_ckpt_link_path = os.path.join(
        Root, "sessions", session_name, session_name + ".ckpt")
    if not os.path.exists(session_ckpt_link_path):
        os.symlink(session_ckpt_link_path,
                   os.path.join(MODEL_DIR, session_name + ".ckpt"))
    model_path = MODEL_DIR

    scheduler = DDIMScheduler(beta_start=0.00085, beta_end=0.012,
                              beta_schedule="scaled_linear", clip_sample=False, set_alpha_to_one=False)
    pipe = StableDiffusionPipeline.from_pretrained(
        model_path, scheduler=scheduler, safety_checker=None, torch_dtype=torch.float16).to("cuda")

    g_cuda = None

    # @markdown Can set random seed here for reproducibility.
    g_cuda = torch.Generator(device='cuda')
    seed = random.randint(1, 999999)  # @param {type:"number"}
    g_cuda.manual_seed(seed)

    # @title Run for generating images.

    prompt = f"ejxjo"  # @param {type:"string"}
    negative_prompt = ""  # @param {type:"string"}
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

    start_index = len(os.listdir(OUTPUT_DIR))
    for index, img in enumerate(images):
        img.save(os.path.join(OUTPUT_DIR, str(
            start_index + index) + "_" + str(seed) + ".jpg"))
