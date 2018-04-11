FROM nvidia/cuda:9.0-cudnn7-devel-ubuntu16.04

ENV PATH="/usr/local/cuda/bin:/miniconda/bin:${PATH}"
ENV LD_LIBRARY_PATH="/usr/local/nvidia/lib64:/usr/local/nvidia/lib:/usr/local/cuda/lib64:/usr/local/cuda/lib:${LD_LIBRARY_PATH}"
ENV TZ=Asia/Shanghai
RUN echo ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone && \
        DEBIAN_FRONTEND=noninteractive apt-get update && apt-get -y dist-upgrade && \
        DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends apt-utils && \
        DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
            build-essential \
            ca-certificates \
            wget \
            git \
            vim \
            locales \
            language-pack-en \
            tzdata \
            zookeeper \
            ssh \
            libatlas-dev \
            liblapack-dev \
        && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN wget https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh \
        -O /tmp/miniconda.sh \
        && \
    /bin/bash /tmp/miniconda.sh -b -p /miniconda && \
    rm -rf /tmp/miniconda.sh && \
    conda config --set show_channel_urls yes && \
    conda config --set always_yes yes --set changeps1 no && \
    conda update --yes -q conda && \
    conda info -a && \
    conda install -n root _license && \
    conda install --yes -q python=3.6

RUN pip install http://download.pytorch.org/whl/cu90/torch-0.3.1-cp36-cp36m-linux_x86_64.whl torchvision

RUN conda install -c conda-forge pytables
RUN pip install dill pandas


COPY test.py /test.py
COPY train.py /train.py
