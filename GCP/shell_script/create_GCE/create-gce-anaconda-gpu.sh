#!/bin/bash

# -------- CONFIG --------
INSTANCE_NAME="ubuntu-anaconda-gpu"
ZONE="us-central1-a"
IMAGE_FAMILY="ubuntu-2404-lts"
IMAGE_PROJECT="ubuntu-os-cloud"
MACHINE_TYPE="n1-standard-4"
STARTUP_SCRIPT="gce-startup-anaconda-gpu.sh"
FILES_FOLDER="gce-files"

# -------- PREPARE --------
mkdir -p "$FILES_FOLDER"
cp llm_110623.yml "$FILES_FOLDER/"
cp web_scrape_etl.yml "$FILES_FOLDER/"

cat > "$FILES_FOLDER/$STARTUP_SCRIPT" << 'EOF'
#!/bin/bash
set -e

# System prep
sudo apt update && sudo apt upgrade -y
sudo apt install -y wget bzip2 git build-essential dkms

# Install NVIDIA drivers and CUDA toolkit
sudo apt install -y ubuntu-drivers-common
sudo ubuntu-drivers autoinstall

# Install Anaconda
cd /tmp
wget https://repo.anaconda.com/archive/Anaconda3-2024.02-1-Linux-x86_64.sh -O anaconda.sh
bash anaconda.sh -b -p /opt/anaconda
echo 'export PATH="/opt/anaconda/bin:$PATH"' >> /etc/profile.d/anaconda.sh
source /opt/anaconda/bin/activate

# Create conda envs
mkdir -p /opt/setup
cp /tmp/llm_110623.yml /opt/setup/
cp /tmp/web_scrape_etl.yml /opt/setup/
/opt/anaconda/bin/conda env create -f /opt/setup/llm_110623.yml
/opt/anaconda/bin/conda env create -f /opt/setup/web_scrape_etl.yml
EOF

# -------- CREATE INSTANCE --------
gcloud compute instances create "$INSTANCE_NAME" \
  --zone="$ZONE" \
  --image-family="$IMAGE_FAMILY" \
  --image-project="$IMAGE_PROJECT" \
  --machine-type="$MACHINE_TYPE" \
  --accelerator=type=nvidia-tesla-t4,count=1 \
  --maintenance-policy=TERMINATE \
  --metadata-from-file startup-script="$FILES_FOLDER/$STARTUP_SCRIPT" \
  --scopes=https://www.googleapis.com/auth/cloud-platform \
  --boot-disk-size=100GB \
  --metadata="install-nvidia-driver=True"

# -------- COPY YAML FILES --------
echo "Waiting for instance to initialize..."
sleep 30
gcloud compute scp llm_110623.yml web_scrape_etl.yml "$INSTANCE_NAME":/tmp/ --zone="$ZONE"
