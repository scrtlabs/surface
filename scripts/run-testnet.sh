#!/bin/bash

set -eux

N=${1:-4}
MPWD=$(pwd)

docker network create \
  --driver=bridge \
  --subnet=172.75.0.0/16 \
  --ip-range=172.75.5.0/24 \
  --gateway=172.75.5.254 \
  enigmanet

