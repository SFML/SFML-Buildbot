#!/bin/bash

wget https://github.com/crazy-max/binfmt/archive/e12c82ce0b82905780d3c12d4bfed4f6a59b0391.zip
unzip e12c82ce0b82905780d3c12d4bfed4f6a59b0391.zip
cd binfmt-e12c82ce0b82905780d3c12d4bfed4f6a59b0391
docker buildx bake --load mainline
docker run --privileged --rm tonistiigi/binfmt:test --install all
docker run --privileged --rm tonistiigi/binfmt:test --version
cd ..
rm -rf binfmt-e12c82ce0b82905780d3c12d4bfed4f6a59b0391 e12c82ce0b82905780d3c12d4bfed4f6a59b0391.zip
