#!/bin/bash

docker run -it --rm --net enigmanet -p 3010:3000 --ip 172.75.5.12 --name dapp mvp0/dapp
