#!/bin/bash

# -------- CONFIG --------
INSTANCE_NAME="ubuntu-anaconda-gpu-spot"
ZONES=("us-central1-a" "us-central1-b" "us-central1-c" "us-central1-f" "us-east1-c" "us-east1-d" "us-east4-a" "us-east4-b" "us-east4-c" "us-west1-a" "us-west1-b" "us-west2-c" "us-west3-b" "us-west4-a" "us-west4-b")
IMAGE_FAMILY="ubuntu-2204-lts"
IMAGE_PROJECT="ubuntu-os-cloud"
MACHINE_TYPE="n1-standard-4"
STARTUP_SCRIPT="gce-startup-anaconda-gpu-spot.sh"
FILES_FOLDER="gce-files"

# -------- PREPARE --------
mkdir -p "$FILES_FOLDER"
cp llm_110623.yml "$FILES_FOLDER/"
cp web_scrape_etl.yml "$FILES_FOLDER/"

cat > "$FILES_FOLDER/$STARTUP_SCRIPT" << 'EOF'
#!/bin/bash
exec > /var/log/startup-script.log 2>&1
set -ex

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

# Clone repos
mkdir -p /home/scotsditch/repos
cd /home/scotsditch/repos
git clone https://github.com/scotsditch/ScotShieldsWorkSamples.git
chmod 777 -R /home/scotsditch/repos

sleep 300

# Create conda envs
mkdir -p /opt/setup
cp /tmp/llm_110623.yml /opt/setup/
cp /tmp/web_scrape_etl.yml /opt/setup/

/opt/anaconda/bin/conda env create -f /opt/setup/web_scrape_etl.yml
sleep 300
/opt/anaconda/bin/conda env create -f /opt/setup/llm_110623.yml
EOF


# --------Old Create instance versions ---------

# # -------- CREATE INSTANCE --------
# gcloud compute instances create "$INSTANCE_NAME" \
#   --preemptible \
#   --provisioning-model=SPOT \
#   --zone="$ZONE" \
#   --image-family="$IMAGE_FAMILY" \
#   --image-project="$IMAGE_PROJECT" \
#   --machine-type="$MACHINE_TYPE" \
#   --accelerator=type=nvidia-tesla-t4,count=1 \
#   --maintenance-policy=TERMINATE \
#   --metadata-from-file startup-script="$FILES_FOLDER/$STARTUP_SCRIPT" \
#   --scopes=https://www.googleapis.com/auth/cloud-platform \
#   --boot-disk-size=100GB \
#   --metadata="install-nvidia-driver=True"


# # -------- CREATE INSTANCE --------
# gcloud compute instances create "$INSTANCE_NAME" \
#   --zone="$ZONE" \
#   --image-family="$IMAGE_FAMILY" \
#   --image-project="$IMAGE_PROJECT" \
#   --machine-type="$MACHINE_TYPE" \
#   --accelerator=type=nvidia-tesla-t4,count=1 \
#   --maintenance-policy=TERMINATE \
#   --metadata-from-file startup-script="$FILES_FOLDER/$STARTUP_SCRIPT" \
#   --scopes=https://www.googleapis.com/auth/cloud-platform \
#   --boot-disk-size=100GB \
#   --metadata="install-nvidia-driver=True"


# gcloud compute instances create "$INSTANCE_NAME" \
#   --zone="$ZONE" \
#   --image-family="$IMAGE_FAMILY" \
#   --image-project="$IMAGE_PROJECT" \
#   --machine-type="$MACHINE_TYPE" \
#   --metadata-from-file startup-script="$FILES_FOLDER/$STARTUP_SCRIPT" \
#   --scopes=https://www.googleapis.com/auth/cloud-platform \
#   --boot-disk-size=100GB

# -------- CREATE INSTANCE WITH ZONE FALLBACK --------
INSTANCE_CREATED=0
for ZONE in "${ZONES[@]}"; do
  echo "Trying to create instance in $ZONE..."
  if gcloud compute instances create "$INSTANCE_NAME" \
    --zone="$ZONE" \
    --image-family="$IMAGE_FAMILY" \
    --image-project="$IMAGE_PROJECT" \
    --machine-type="$MACHINE_TYPE" \
    --accelerator=type=nvidia-tesla-t4,count=2 \
    --maintenance-policy=TERMINATE \
    --metadata-from-file startup-script="$FILES_FOLDER/$STARTUP_SCRIPT" \
    --scopes=https://www.googleapis.com/auth/cloud-platform \
    --boot-disk-size=100GB \
    --metadata="install-nvidia-driver=True" \
    --preemptible; then

    INSTANCE_CREATED=1
    echo "Instance created successfully in $ZONE"
    break
  else
    echo "Failed to create instance in $ZONE, trying next zone..."
  fi
done

if [ "$INSTANCE_CREATED" -eq 0 ]; then
  echo "ERROR: Failed to create instance in all specified zones. Exiting."
  exit 1
fi

# -------- COPY YAML FILES TO INSTANCE --------
echo "Waiting for instance to initialize..."
sleep 30
gcloud compute scp llm_110623.yml web_scrape_etl.yml "$INSTANCE_NAME":/tmp/ --zone="$ZONE"
