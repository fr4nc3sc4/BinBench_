FROM ubuntu:20.04
ARG VERSION

#FOR GCC 3.4
RUN if [ "$VERSION" = "3.4" ]; then \
    apt-get -y update && apt-get -y install build-essential  && \
    echo 'deb     http://snapshot.debian.org/archive/debian/20070730T000000Z/ lenny main' | tee -a /etc/apt/sources.list && \
####
#RUN echo 'deb-src http://snapshot.debian.org/archive/debian/20070730T000000Z/ lenny main' | tee -a /etc/apt/sources.list
#RUN echo 'deb     http://snapshot.debian.org/archive/debian-security/20070730T000000Z/ lenny/updates main' | tee -a /etc/apt/sources.list
#RUN echo 'deb-src http://snapshot.debian.org/archive/debian-security/20070730T000000Z/ lenny/updates main' | tee -a /etc/apt/sources.list
####
    apt-get update --allow-insecure-repositories && \
    apt-get -y --allow-unauthenticated install gcc-3.4 && \
    apt-get -y --allow-unauthenticated install g++-3.4 && \
    update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-9 0 && \
    update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-3.4 1 && \
    update-alternatives --install /usr/bin/g++ g++ /usr/bin/g++-9 0 && \
    update-alternatives --install /usr/bin/g++ g++ /usr/bin/g++-3.4 1; \
#FOR GCC 4.7
elif [ "$VERSION" = "4.7" ]; then \
    apt-get -y update && apt-get -y install build-essential  && \
    echo 'deb http://old-releases.ubuntu.com/ubuntu quantal main' | tee /etc/apt/sources.list && \
    apt-get update --allow-insecure-repositories && \
    apt-get -y install gcc-4.7 && \
    apt-get -y install g++-4.7 && \
    update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-9 0 && \
    update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-4.7 1 && \
    update-alternatives --install /usr/bin/g++ g++ /usr/bin/g++-9 0 && \
    update-alternatives --install /usr/bin/g++ g++ /usr/bin/g++-4.7 1; \
#FOR GCC 5.0
elif [ "$VERSION" = "5" ]; then \
    apt-get -y update && apt-get -y install build-essential  && \
    echo 'deb http://old-releases.ubuntu.com/ubuntu wily main' | tee /etc/apt/sources.list && \
    apt-get update && \
    apt-get -y install gcc-5 && \
    apt-get -y install g++-5 && \
    update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-9 0 && \
    update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-5 1 && \
    update-alternatives --install /usr/bin/g++ g++ /usr/bin/g++-9 0 && \
    update-alternatives --install /usr/bin/g++ g++ /usr/bin/g++-5 1 ; \
else \
    echo 'wrong version'; \
fi

#BUILD:
#docker build -t docker-gcc --build-arg VERSION="version number ( 3.4 / 4.7 / 5 )" .
#RUN:
#docker run --name container-name -it -v folder-path-in-os:/volume-name-in-container docker-gcc
