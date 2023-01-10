# install pip
# wget -O scripts/train_dreambooth.py https://github.com/ShivamShrirao/diffusers/raw/main/examples/dreambooth/train_dreambooth.py
wget -O scripts/convert_diffusers_to_original_stable_diffusion.py https://github.com/ShivamShrirao/diffusers/raw/main/scripts/convert_diffusers_to_original_stable_diffusion.py
# wget -O scripts/convertosd.py https://github.com/TheLastBen/fast-stable-diffusion/raw/main/Dreambooth/convertosd.py
# wget -O scripts/convertodiffv1.py https://github.com/TheLastBen/fast-stable-diffusion/raw/main/Dreambooth/convertodiffv1.py




sudo apt update && sudo apt install python3-pip git-lfs rabbitmq-server

pip install git+https://github.com/ShivamShrirao/diffusers
pip install -U --pre triton
pip install accelerate==0.12.0 transformers ftfy bitsandbytes gradio natsort
pip install https://github.com/brian6091/xformers-wheels/releases/download/0.0.15.dev0%2B4c06c79/xformers-0.0.15.dev0+4c06c79.d20221205-cp38-cp38-linux_x86_64.whl
pip install torchvision tqdm pika python-dotenv supabase boto3 logtail-python

# Download model
mkdir stable-diffusion-v1-5
cd stable-diffusion-v1-5
# install git lfs
git init
sudo git lfs install --system --skip-repo
git remote add -f origin  "https://USER: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@huggingface.co/runwayml/stable-diffusion-v1-5"
git config core.sparsecheckout true
echo -e "scheduler\ntext_encoder\ntokenizer\nunet\nmodel_index.json" > .git/info/sparse-checkout
git pull origin main
git clone "https://USER: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@huggingface.co/stabilityai/sd-vae-ft-mse"
mv sd-vae-ft-mse vae
sudo rm -r .git
rm model_index.json
wget https://raw.githubusercontent.com/TheLastBen/fast-stable-diffusion/main/Dreambooth/model_index.json
sed -i 's@"clip_sample": false@@g' scheduler/scheduler_config.json
sed -i 's@"trained_betas": null,@"trained_betas": null@g' scheduler/scheduler_config.json
sed -i 's@"sample_size": 256,@"sample_size": 512,@g' vae/config.json  

mkdir sessions
mkdir models

sudo mkdir /content
sudo wget -O /content/refmdlz https://github.com/TheLastBen/fast-stable-diffusion/raw/main/Dreambooth/refmdlz
sudo unzip -o -q /content/refmdlz -d /content
sudo rm -f /content/refmdlz

echo -e "[default]\nregion=eu-south-1" > ~/.aws/config
echo "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" > ~/.huggingface

sudo ln /home/ubuntu/avatarify-ai-ml/start_train.service /etc/systemd/system/train.service
sudo systemctl daemon-reload
sudo systemctl enable train.service
sudo systemctl start train.service

sudo ln /home/ubuntu/avatarify-ai-ml/start_generate.service /etc/systemd/system/generate.service
sudo systemctl daemon-reload
sudo systemctl enable generate.service
sudo systemctl start generate.service

sudo ln /home/ubuntu/avatarify-ai-ml/start_train_and_generate.service /etc/systemd/system/train_and_generate.service
sudo systemctl daemon-reload
sudo systemctl enable train_and_generate.service
sudo systemctl start train_and_generate.service

sudo systemctl stop XXX.service