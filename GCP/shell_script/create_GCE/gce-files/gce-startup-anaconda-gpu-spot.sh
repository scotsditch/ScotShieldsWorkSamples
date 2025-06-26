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
