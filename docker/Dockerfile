FROM archlinux:latest

# Provide the predefined image compiler from command line.
ARG C_COMPILER_NAME
ARG CXX_COMPILER_NAME
ARG COMPILER_VERSION
ARG PACKAGE_NAME

# Install packages required for the building process.
RUN pacman -Syu --noconfirm; \
pacman -Sy --noconfirm asp base-devel;

# Create the binbench user and allow it to always run sudo.
RUN useradd -ms /bin/bash binbench; \
groupadd sudo; \
usermod -aG sudo binbench; \
echo "%sudo ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers;

# Execute commands as the binbench user from now on.
USER binbench
WORKDIR /home/binbench

# Update pacman configuration to support arch4edu mirror.
RUN sudo pacman-key --init; \
echo "[arch4edu]" | sudo tee -a /etc/pacman.conf; \
echo "Server = https://mirror.lesviallon.fr/arch4edu/x86_64" | sudo tee -a /etc/pacman.conf;

# Install the arch4edu keyring.
RUN git clone https://aur.archlinux.org/arch4edu-keyring.git; \
cd arch4edu-keyring; \
makepkg -si --noconfirm; \
rm -rf ../arch4edu-keyring; \
sudo pacman -Syu --noconfirm;

# Install the predefined gcc version for the image. gcc-10 is installed already as a base-devel component.
RUN \
# Install an older version for gcc from the arch4edu mirror.
if [[ $C_COMPILER_NAME == "gcc" && $COMPILER_VERSION != "10" ]]; then \
	sudo pacman -Sy --noconfirm $PACKAGE_NAME; \
	# Update system symlinks to reflect compiler changes.
	sudo ln -fs $(which $C_COMPILER_NAME-$COMPILER_VERSION) /usr/bin/$C_COMPILER_NAME; \
	sudo ln -fs $(which $C_COMPILER_NAME-$COMPILER_VERSION) /usr/sbin/$C_COMPILER_NAME; \
	sudo ln -fs $(which $CXX_COMPILER_NAME-$COMPILER_VERSION) /usr/bin/$CXX_COMPILER_NAME; \
	sudo ln -fs $(which $CXX_COMPILER_NAME-$COMPILER_VERSION) /usr/sbin/$CXX_COMPILER_NAME; \
fi

# Install the predefined clang version for the image.
RUN \
if [[ $C_COMPILER_NAME == "clang" ]]; then \
	# Install older clang versions from binaries.
	if [[ $COMPILER_VERSION != "11" ]]; then \
		sudo pacman -Sy --noconfirm wget ncurses5-compat-libs; \
		wget $PACKAGE_NAME; \
		package_name=${PACKAGE_NAME##*/}; \
		tar -xf $package_name; \
		sudo cp -R ./${package_name%.tar.xz}/* /usr/local; \
		rm -rf ./*; \
	else \
		# Install clang latest version from Arc linux official mirrors.
		sudo pacman -Sy --noconfirm clang; \
	fi \
fi

# Update makepkg configuration to support the predefined image compiler.
RUN echo "export CC=$C_COMPILER_NAME" | sudo tee -a /etc/makepkg.conf; \
echo "export CXX=$CXX_COMPILER_NAME" | sudo tee -a /etc/makepkg.conf;