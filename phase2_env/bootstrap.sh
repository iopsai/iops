#!/usr/bin/env bash


# install language pack
apt update
apt upgrade -y
apt install language-pack-en -y


# install docker-ce
apt-get install     apt-transport-https     ca-certificates     curl     software-properties-common -y
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo add-apt-repository    "deb [arch=amd64] https://download.docker.com/linux/ubuntu \
   $(lsb_release -cs) \
   stable" -y
apt-get update
apt-get install docker-ce -y


# install cuda
wget http://developer.download.nvidia.com/compute/cuda/repos/ubuntu1604/x86_64/cuda-repo-ubuntu1604_9.1.85-1_amd64.deb  -O /tmp/cuda-repo-ubuntu1604-9-1-local_9.1.85-1_amd64.deb
dpkg -i /tmp/cuda-repo-ubuntu1604-9-1-local_9.1.85-1_amd64.deb
apt-key adv --fetch-keys http://developer.download.nvidia.com/compute/cuda/repos/ubuntu1604/x86_64/7fa2af80.pub
apt-get update
apt-get install cuda -y
# install nvidia-docker

# If you have nvidia-docker 1.0 installed: we need to remove it and all existing GPU containers
docker volume ls -q -f driver=nvidia-docker | xargs -r -I{} -n1 docker ps -q -a -f volume={} | xargs -r docker rm -f
apt-get purge -y nvidia-docker
# Add the package repositories
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | \
  apt-key add -
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | \
  tee /etc/apt/sources.list.d/nvidia-docker.list
apt-get update
# Install nvidia-docker2 and reload the Docker daemon configuration
apt-get install -y nvidia-docker2
pkill -SIGHUP dockerd
# Test nvidia-smi with the latest official CUDA image
docker run --runtime=nvidia --rm nvidia/cuda nvidia-smi


# install miniconda
export PATH="/usr/local/cuda/bin:/miniconda/bin:${PATH}"
echo "export PATH=\"/usr/local/cuda/bin:/miniconda/bin:${PATH}\"" >> ~/.bashrc
echo "export LC_ALL=C.UTF-8" >> ~/.bashrc
echo "export LANG=C.UTF-8" >> ~/.bashrc
source ~/.bashrc
wget https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh \
        -O /tmp/miniconda.sh \
        && \
    /bin/bash /tmp/miniconda.sh -u -b -p /miniconda && \
    rm -rf /tmp/miniconda.sh && \
    conda config --set show_channel_urls yes && \
    conda config --set always_yes yes --set changeps1 no && \
    conda update --yes -q conda && \
    conda info -a && \
    conda install -n root _license && \
    conda install --yes -q python=3.6
conda install click pandas --yes
pip install sklearn scipy tables
