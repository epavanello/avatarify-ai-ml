import os
import random
import shutil
from PIL import Image
from subprocess import getoutput
from scripts import convertosd
from scripts import train_dreambooth

Root = os.getcwd()

Crop_images = True
Crop_size = 512


def dump_only_textenc(MODELT_NAME, INSTANCE_DIR, OUTPUT_DIR, PT: str = None, Seed: int = None, precision: str = None, Training_Steps: int = None):
    train_dreambooth.Run(train_text_encoder=True,
                         pretrained_model_name_or_path=MODELT_NAME,
                         instance_data_dir=INSTANCE_DIR,
                         output_dir=OUTPUT_DIR,
                         instance_prompt=PT,
                         seed=Seed,
                         resolution=512,
                         mixed_precision=precision,
                         train_batch_size=1,
                         gradient_accumulation_steps=1,
                         gradient_checkpointing=True,
                         use_8bit_adam=True,
                         learning_rate=2e-6,
                         lr_scheduler="polynomial",
                         lr_warmup_steps=0,
                         max_train_steps=Training_Steps)


def train_only_unet(stpsv, stp, SESSION_DIR, MODELT_NAME, INSTANCE_DIR, OUTPUT_DIR, PT, Seed, Res, precision, Training_Steps):
    train_dreambooth.Run(
        pretrained_model_name_or_path=MODELT_NAME,
        instance_data_dir=INSTANCE_DIR,
        output_dir=OUTPUT_DIR,
        instance_prompt=PT,
        seed=Seed,
        resolution=Res,
        mixed_precision=precision,
        train_batch_size=1,
        gradient_accumulation_steps=1,
        learning_rate=2e-6,
        lr_scheduler="polynomial",
        lr_warmup_steps=0,
        max_train_steps=Training_Steps)


def train(session_Name):
    MODEL_NAME = os.path.join(Root, "stable-diffusion-v1-5")
    PT = ""
    INSTANCE_NAME = session_Name
    OUTPUT_DIR = os.path.join(Root, "models", session_Name)
    SESSION_DIR = os.path.join(Root, 'sessions', session_Name)
    INSTANCE_DIR = os.path.join(SESSION_DIR, 'instance_images')
    MDLPTH = os.path.join(SESSION_DIR, session_Name+'.ckpt')

    os.makedirs(INSTANCE_DIR, exist_ok=True)
    print('Session created, proceed to uploading instance images')

    for subdir, dirs, files in os.walk(INSTANCE_DIR):
        for filename in files:
            # print os.path.join(subdir, file)
            filepath = subdir + os.sep + filename
            extension = filename.split(".")[1]
            file = Image.open(filepath)
            width, height = file.size
            if file.size != (Crop_size, Crop_size):
                side_length = min(width, height)
                left = (width - side_length)/2
                top = (height - side_length)/2
                right = (width + side_length)/2
                bottom = (height + side_length)/2
                image = file.crop((left, top, right, bottom))
                image = image.resize((Crop_size, Crop_size))
                if (extension.upper() == "JPG"):
                    image.save(filepath, format="JPEG", quality=100)
                else:
                    image.save(filepath, format=extension.upper())

    # prepare training
    # TODO restore: It was * 100
    UNet_Training_Steps = len(files) * 1
    Seed = random.randint(1, 999999)
    fp16 = True
    if fp16:
        prec = "fp16"
    else:
        prec = "no"
    # TODO restore: It was 350
    Text_Encoder_Training_Steps = 0
    Resolution = 512

    s = getoutput('nvidia-smi')
    if 'A100' in s:
        precision = "no"
    else:
        precision = prec
    prc = "--fp16" if precision == "fp16" else ""

    if os.path.exists(os.path.join(OUTPUT_DIR, 'text_encoder_trained')):
        shutil.rmtree(os.path.join(OUTPUT_DIR, 'text_encoder_trained'))

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    create_symlink('models', OUTPUT_DIR)
    create_symlink('scheduler', OUTPUT_DIR)
    create_symlink('sessions', OUTPUT_DIR)
    create_symlink('text_encoder', OUTPUT_DIR)
    create_symlink('tokenizer', OUTPUT_DIR)
    create_symlink('unet', OUTPUT_DIR)
    create_symlink('vae', OUTPUT_DIR)
    create_symlink('model_index.json', OUTPUT_DIR)

    if Text_Encoder_Training_Steps > 0:
        dump_only_textenc(MODEL_NAME, INSTANCE_DIR, OUTPUT_DIR,
                          PT, None, precision, Training_Steps=Text_Encoder_Training_Steps)

    Start_saving_from_the_step = 500

    train_only_unet(Start_saving_from_the_step, 0, SESSION_DIR, MODEL_NAME, INSTANCE_DIR,
                    OUTPUT_DIR, PT, Seed, Resolution, precision, Training_Steps=UNet_Training_Steps)

    convertosd.Run(OUTPUT_DIR, SESSION_DIR, session_Name)


def create_symlink(name: str, destination_dir: str):
    if not os.path.exists(os.path.join(destination_dir, name)):
        os.symlink(os.path.join(Root, "stable-diffusion-v1-5", name),
                   os.path.join(destination_dir, name))
