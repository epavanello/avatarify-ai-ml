import os
import shutil
import time
from tqdm import tqdm
from PIL import Image
from subprocess import getoutput

Root = '/home/ubuntu/dreambooth/'

WORKSPACE = Root + 'Fast-Dreambooth'
Crop_images = True
Crop_size = 512


def train(Session_Name="emanuele"):

    INSTANCE_NAME = Session_Name
    OUTPUT_DIR = Root + "models/"+Session_Name
    SESSION_DIR = WORKSPACE+'/Sessions/'+Session_Name
    INSTANCE_DIR = SESSION_DIR+'/instance_images'
    MDLPTH = str(SESSION_DIR+"/"+Session_Name+'.ckpt')

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
        UNet_Training_Steps=len(files) * 100
        fp16 = True
        if fp16:
            prec="fp16"
        else:
            prec="no"
        Text_Encoder_Training_Steps=350
        Resolution=512

        s = getoutput('nvidia-smi')
        if 'A100' in s:
            precision="no"
        else:
            precision=prec
        prc="--fp16" if precision=="fp16" else ""

        from scripts.convertosd import convertosd

        convertosd(OUTPUT_DIR, SESSION_DIR, Session_Name)
        




if __name__ == "__main__":
    train()
