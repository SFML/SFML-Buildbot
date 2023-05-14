#!/bin/bash

wget https://downloads.raspberrypi.org/raspios_lite_arm64/images/raspios_lite_arm64-2023-05-03/2023-05-03-raspios-bullseye-arm64-lite.img.xz
xz -d 2023-05-03-raspios-bullseye-arm64-lite.img.xz
fdisk -l 2023-05-03-raspios-bullseye-arm64-lite.img 
tmpdir=$(mktemp -u)
mkdir -p $tmpdir
mount -t auto -o loop,offset=$((532480*512)) 2023-05-03-raspios-bullseye-arm64-lite.img $tmpdir
tar -cf rootfs.tar --exclude="dev/*" --exclude="proc/*" --exclude="sys/*" --exclude="tmp/*" --exclude="run/*" --exclude="mnt/*" --exclude="media/*" --exclude="lost+found" -C $tmpdir/ .
umount $tmpdir
rmdir $tmpdir
rm 2023-05-03-raspios-bullseye-arm64-lite.img*
docker import rootfs.tar raspberry-pi-os-base:latest
rm rootfs.tar
docker buildx build -t buildbot-worker-rpi:latest - < Dockerfile
