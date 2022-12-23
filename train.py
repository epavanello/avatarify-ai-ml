import os
import random
import shutil
from PIL import Image
from subprocess import getoutput
from scripts import convertosd
from scripts import train_dreambooth
from scripts import train_dreambooth_new

Root = os.getcwd()

Crop_images = True
Crop_size = 512


def txtenc_train(MODELT_NAME, INSTANCE_DIR, CLASS_DIR, OUTPUT_DIR, PT, Seed, precision, GC, Training_Steps):
    print('[1;33mTraining the text encoder with regularization...[0m')
    train_dreambooth.Run(
        pretrained_model_name_or_path=MODELT_NAME,
        instance_data_dir=INSTANCE_DIR,
        class_data_dir=CLASS_DIR,
        output_dir=OUTPUT_DIR,
        with_prior_preservation=True,
        prior_loss_weight=1.0,
        instance_prompt=PT,
        seed=Seed,
        resolution=512,
        mixed_precision=precision,
        train_batch_size=1,
        gradient_accumulation_steps=1,
        use_8bit_adam=True,
        learning_rate=2e-6,
        lr_scheduler="polynomial",
        lr_warmup_steps=0,
        max_train_steps=Training_Steps,
        num_class_images=200
    )


def train(session_name: str):
    MODEL_NAME = os.path.join(Root, "stable-diffusion-v1-5")
    PT = ""
    INSTANCE_NAME = session_name
    OUTPUT_DIR = os.path.join(Root, "models", session_name)
    SESSION_DIR = os.path.join(Root, 'sessions', session_name)
    INSTANCE_DIR = os.path.join(SESSION_DIR, 'instance_images')
    MDLPTH = os.path.join(SESSION_DIR, session_name+'.ckpt')
    CLASS_DIR = os.path.join(SESSION_DIR, 'Regularization_images')

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
    UNet_Training_Steps = len(files) * 100
    UNet_Learning_Rate = 2e-6 #@param ["1e-6","2e-6","3e-6","4e-6","5e-6"] {type:"raw"}
    untlr=UNet_Learning_Rate
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

    # Training text encoder
    # dump_only_textenc()
    train_dreambooth_new.Run(
        train_dreambooth_new.Get_args().parse_args([
            "--image_captions_filename",
            "--train_text_encoder",
            "--dump_only_text_encoder",
            f"--pretrained_model_name_or_path=\"{MODEL_NAME}\"",
            f"--instance_data_dir=\"{INSTANCE_DIR}\"",
            f"--output_dir=\"{OUTPUT_DIR}\"",
            f"--instance_prompt=\"{PT}\"",
            f"--seed={Seed}",
            "--resolution=512",
            f"--mixed_precision={precision}",
            "--train_batch_size=1",
            "--gradient_accumulation_steps=1",
            GC,
            "--use_8bit_adam",
            f"--learning_rate={txlr}",
            "--lr_scheduler=\"polynomial\"",
            "--lr_warmup_steps=0",
            f"--max_train_steps={Text_Encoder_Training_Steps}"
        ])
    )

    Start_saving_from_the_step = 500

    # Training the UNet
    # train_only_unet
    # def train_only_unet(stpsv, stp, SESSION_DIR, MODELT_NAME, INSTANCE_DIR, OUTPUT_DIR, PT, Seed, Res, precision, Training_Steps):
    train_dreambooth_new.Run(
        train_dreambooth_new.Get_args().parse_args([
            "--image_captions_filename",
            "--train_only_unet",
            "--save_starting_step=$stpsv",
            "--save_n_steps=$stp",
            "--Session_dir=$SESSION_DIR",
            f"--pretrained_model_name_or_path=\"{MODEL_NAME}\"",
            f"--instance_data_dir=\"{INSTANCE_DIR}\"",
            f"--output_dir=\"{OUTPUT_DIR}\"",
            f"--instance_prompt=\"{PT}\"",
            f"--seed={Seed}",
            f"--resolution={Res}",
            f"--mixed_precision={precision}",
            "--train_batch_size=1",
            "--gradient_accumulation_steps=1",
            GC,
            "--use_8bit_adam",
            f"--learning_rate={untlr}",
            "--lr_scheduler=\"polynomial\"",
            "--lr_warmup_steps=0",
            f"--max_train_steps={UNet_Training_Steps}"
        ])
    )

    convertosd.Run(OUTPUT_DIR, SESSION_DIR, session_name)


def create_symlink(name: str, destination_dir: str):
    if not os.path.exists(os.path.join(destination_dir, name)):
        os.symlink(os.path.join(Root, "stable-diffusion-v1-5", name),
                   os.path.join(destination_dir, name))
