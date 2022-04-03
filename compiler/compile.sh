#!/bin/bash

BASE_DIR=$(pwd)

# Specify the optimization level using makepkg configuration.
sudo sed -i "s/CPPFLAGS=\".*\"/CPPFLAGS=\"-$OPT -g\"/" /etc/makepkg.conf
sudo sed -i "s/CFLAGS=\".*\"/CFLAGS=\"-$OPT -g\"/" /etc/makepkg.conf
sudo sed -i "s/CXXFLAGS=\".*\"/CXXFLAGS=\"-$OPT -g\"/" /etc/makepkg.conf
sudo sed -i "s/LDFLAGS=\".*\"/LDFLAGS=\"-$OPT -g\"/" /etc/makepkg.conf

# Build project
mkdir build
cd build
asp checkout $PACKAGE_NAME
cd $PACKAGE_NAME
asp update
git pull
cd trunk
makepkg -f --syncdeps --skippgpcheck --noconfirm

# Copy compiled files inside the shared directory.
mkdir -p "$BASE_DIR/elf/$OPT"
find ./ -name "*.o" | xargs cp -n -t "$BASE_DIR/elf/$OPT"