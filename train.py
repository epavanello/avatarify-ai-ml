import base64
import io
import os
import random
import shutil
import subprocess
from typing import List
from subprocess import getoutput
from PIL import Image
from supabase import Client
from datetime import datetime
import config
import s3

from pydantic import BaseModel

Root = os.getcwd()

Crop_images = True
Crop_size = 512


class TrainImage(BaseModel):
    base64: str
    filename: str


class TrainPayload(BaseModel):
    images: List[TrainImage]


def train(session_name: str, images: List[TrainImage]):
    PT = f"ojwxwjo"
    MODEL_DIR = os.path.join(Root, "models", session_name)
    SESSION_DIR = os.path.join(Root, 'sessions', session_name)
    INSTANCE_DIR = os.path.join(SESSION_DIR, 'instance_images')
    MODEL_PATH = os.path.join(SESSION_DIR, session_name + '.ckpt')

    supabase: Client = config.getSupabase()

    supabase.from_("user_info").update(
        {
            "start_training": datetime.now().isoformat(),
            "in_training": True,
            "trained": False,
            "end_training": None
        }).eq("id", session_name).execute()

    if os.path.exists(INSTANCE_DIR):
        shutil.rmtree(INSTANCE_DIR)
    os.makedirs(INSTANCE_DIR, exist_ok=True)

    if os.path.exists(MODEL_DIR):
        shutil.rmtree(MODEL_DIR)
    os.makedirs(MODEL_DIR, exist_ok=True)

    if os.path.exists(os.path.join(MODEL_DIR, 'text_encoder_trained')):
        shutil.rmtree(os.path.join(MODEL_DIR, 'text_encoder_trained'))

    for index, image in enumerate(images):
        extension = image.filename.split(".")[-1]
        file = Image.open(io.BytesIO(base64.b64decode(image.base64)))
        width, height = file.size
        if file.size != (Crop_size, Crop_size):
            side_length = min(width, height)
            left = (width - side_length)/2
            top = (height - side_length)/2
            right = (width + side_length)/2
            bottom = (height + side_length)/2
            file = file.crop((left, top, right, bottom))
            file = file.resize((Crop_size, Crop_size))
        if (extension.upper() == "JPG"):
            file.save(os.path.join(INSTANCE_DIR, "ojwxwjo" + " (" + str(index + 1) + ").jpg"),
                      format="JPEG", quality=100)
        else:
            file.save(os.path.join(INSTANCE_DIR, "ojwxwjo" + " (" + str(index + 1) + ")." + extension),
                      format=extension.upper())

    # prepare training
    # TODO restore: It was * 100
    UNet_Training_Steps = len(images) * 100
    # @param ["1e-6","2e-6","3e-6","4e-6","5e-6"] {type:"raw"}
    UNet_Learning_Rate = 2e-6
    untlr = UNet_Learning_Rate
    Seed = random.randint(1, 999999)

    # @param ["1e-6","8e-7","6e-7","5e-7","4e-7"] {type:"raw"}
    Text_Encoder_Learning_Rate = 1e-6
    txlr = Text_Encoder_Learning_Rate

    fp16 = True

    GC = "--gradient_checkpointing"

    if fp16:
        prec = "fp16"
    else:
        prec = "no"
    s = getoutput('nvidia-smi')
    if 'A100' in s:
        GC = ""

    s = getoutput('nvidia-smi')
    if 'A100' in s:
        precision = "no"
    else:
        precision = prec

    # TODO restore: It was 350
    Text_Encoder_Training_Steps = 350
    Resolution = 512

    copy('scheduler', MODEL_DIR)
    copy('text_encoder', MODEL_DIR)
    copy('tokenizer', MODEL_DIR)
    copy('unet', MODEL_DIR)
    copy('vae', MODEL_DIR)
    copy('model_index.json', MODEL_DIR)

    # 70 was Train_text_encoder_for > https://bytexd.com/how-to-use-dreambooth-to-fine-tune-stable-diffusion-colab/
    stptxt = int((UNet_Training_Steps*70)/100)

    # Training text encoder
    # dump_only_textenc()
    subprocess.run(["python3", os.path.join("scripts", "train_dreambooth.py")] + [
        "--train_text_encoder",
        "--dump_only_text_encoder",
        f"--pretrained_model_name_or_path={MODEL_DIR}",
        f"--instance_data_dir={INSTANCE_DIR}",
        f"--output_dir={MODEL_DIR}",
        f"--instance_prompt={PT}",
        f"--seed={Seed}",
        "--resolution=512",
        f"--mixed_precision={precision}",
        "--train_batch_size=1",
        "--gradient_accumulation_steps=1",
        GC,
        "--use_8bit_adam",
        f"--learning_rate={txlr}",
        "--lr_scheduler=polynomial",
        "--lr_warmup_steps=0",
        # brfore was Text_Encoder_Training_Steps=350
        f"--max_train_steps={stptxt}"
    ], check=True)

    Start_saving_from_the_step = 500
    Save_Checkpoint_Every = 0

    # Training the UNet
    # train_only_unet
    subprocess.run(["python3", os.path.join("scripts", "train_dreambooth.py")] + [
        "--train_only_unet",
        f"--save_starting_step={Start_saving_from_the_step}",
        f"--save_n_steps={Save_Checkpoint_Every}",
        f"--Session_dir={SESSION_DIR}",
        f"--pretrained_model_name_or_path={MODEL_DIR}",
        f"--instance_data_dir={INSTANCE_DIR}",
        f"--output_dir={MODEL_DIR}",
        f"--instance_prompt={PT}",
        f"--seed={Seed}",
        f"--resolution={Resolution}",
        f"--mixed_precision={precision}",
        "--train_batch_size=1",
        "--gradient_accumulation_steps=1",
        GC,
        "--use_8bit_adam",
        f"--learning_rate={untlr}",
        "--lr_scheduler=polynomial",
        "--lr_warmup_steps=0",
        f"--max_train_steps={UNet_Training_Steps}"
    ], check=True)

    subprocess.run(["python3", os.path.join("scripts", "convertosd.py")] + [
        f"--model_path={MODEL_DIR}",
        f"--checkpoint_path={MODEL_PATH}",
    ], check=True)

    s3_client = s3.getS3Client()

    s3_client.upload_file(MODEL_PATH, 'avatarify-ai-storage',
                          os.path.join(session_name, session_name + ".ckpt"))

    supabase.from_("user_info").update(
        {
            "end_training": datetime.now().isoformat(),
            "trained": True,
            "in_training": False
        }).eq("id", session_name).execute()


    shutil.rmtree(MODEL_DIR)
    shutil.rmtree(SESSION_DIR)


def copy(name: str, destination_dir: str):
    from_path = os.path.join(Root, "stable-diffusion-v1-5", name)
    to_path = os.path.join(destination_dir, name)
    if os.path.isdir(from_path):
        if os.path.exists(to_path):
            shutil.rmtree(to_path)
        shutil.copytree(from_path, to_path)
    else:
        shutil.copy(from_path, to_path)
