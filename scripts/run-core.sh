#!/bin/bash

docker run -it --rm --net enigmanet --ip 172.75.5.10 -p 1338:1338 --name core mvp0/core /bin/bash
