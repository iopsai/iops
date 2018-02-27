#!/usr/bin/env bash
DOCKER=nvidia-docker  # nvidia-docker supports GPU
CONTEXT=$(realpath .)
TAG=iops-client
sudo ${DOCKER} build ${CONTEXT} -t ${TAG}
