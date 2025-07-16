FROM debian:stable-slim AS final-layer

RUN DEBIAN_FRONTEND=noninteractive \
    ln -fs /usr/share/zoneinfo/Europe/Berlin /etc/localtime \
    && apt-get update && apt-get install --no-install-recommends -y \
    tzdata \
    curl \
    wget \
    zip \
    unzip \
    git \
    ninja-build \
    build-essential \
    llvm \
    clang \
    libc++-dev \
    libc++abi-dev \
    clang-tools \
    clang-tidy \
    cppcheck \
    lcov \
    gcovr \
    valgrind \
    afl++ \
    libharfbuzz-dev \
    libfreetype-dev \
    libx11-dev \
    libxrandr-dev \
    libxcursor-dev \
    libgl1-mesa-dev \
    libudev-dev \
    libopenal-dev \
    libflac-dev \
    libogg-dev \
    libopus-dev \
    libvorbis-dev \
    libssl-dev \
    python3-pip \
    python3-dev \
    python3-venv \
    xorg-dev \
    x11vnc \
    x11-utils \
    xvfb \
    fluxbox \
    eterm \
    daemonize \
    && apt-get install --no-install-recommends -y libfuzzer-$(clang++ --version | sed -n 's/.*version \([0-9]\+\)\..*/\1/p')-dev \
    && dpkg-reconfigure --frontend noninteractive tzdata \
    && apt-get autoremove -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# CMake
RUN wget https://github.com/Kitware/CMake/releases/download/v3.26.3/cmake-3.26.3.tar.gz \
    && tar xzf cmake-3.26.3.tar.gz \
    && cd cmake-3.26.3 \
    && ./bootstrap --parallel=$(nproc) \
    && make -j $(nproc) install \
    && cmake --version \
    && cd .. \
    && rm -rf cmake-3.26.3*

# pipx
RUN python3 -m pip install --break-system-packages pipx \
    && rm -rf ~/.cache

ENV PATH="$PATH:/root/.local/bin"

# cppclean
RUN pipx install 'cppclean' \
    && rm -rf ~/.cache

# Buildbot Worker
RUN pipx install 'buildbot-worker' \
    && rm -rf ~/.cache

# Test Build GCC
FROM final-layer as test-layer-gcc

RUN wget https://github.com/SFML/SFML/archive/refs/heads/master.zip \
    && unzip master.zip \
    && cd SFML-master \
    && mkdir build \
    && cd build \
    && cmake -DSFML_BUILD_EXAMPLES=TRUE -DSFML_BUILD_TEST_SUITE=TRUE -DCMAKE_BUILD_TYPE=Debug -DBUILD_SHARED_LIBS=TRUE .. && cmake --build . -j8 -- install \
    && cmake -DSFML_BUILD_EXAMPLES=TRUE -DSFML_BUILD_TEST_SUITE=TRUE -DCMAKE_BUILD_TYPE=Debug -DBUILD_SHARED_LIBS=FALSE .. && cmake --build . -j8 -- install \
    && cmake -DSFML_BUILD_EXAMPLES=TRUE -DSFML_BUILD_TEST_SUITE=TRUE -DCMAKE_BUILD_TYPE=Release -DBUILD_SHARED_LIBS=TRUE .. && cmake --build . -j8 -- install \
    && cmake -DSFML_BUILD_EXAMPLES=TRUE -DSFML_BUILD_TEST_SUITE=TRUE -DCMAKE_BUILD_TYPE=Release -DBUILD_SHARED_LIBS=FALSE .. && cmake --build . -j8 -- install

RUN echo "OK" > /verification-gcc.txt

# Test Build Clang
FROM final-layer as test-layer-clang

RUN wget https://github.com/SFML/SFML/archive/refs/heads/master.zip \
    && unzip master.zip \
    && cd SFML-master \
    && mkdir build \
    && cd build \
    && cmake -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++ -DCMAKE_CXX_FLAGS="-stdlib=libc++" -DSFML_BUILD_EXAMPLES=TRUE -DSFML_BUILD_TEST_SUITE=TRUE -DCMAKE_BUILD_TYPE=Debug -DBUILD_SHARED_LIBS=TRUE .. && cmake --build . -j8 -- install \
    && cmake -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++ -DCMAKE_CXX_FLAGS="-stdlib=libc++" -DSFML_BUILD_EXAMPLES=TRUE -DSFML_BUILD_TEST_SUITE=TRUE -DCMAKE_BUILD_TYPE=Debug -DBUILD_SHARED_LIBS=FALSE .. && cmake --build . -j8 -- install \
    && cmake -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++ -DCMAKE_CXX_FLAGS="-stdlib=libc++" -DSFML_BUILD_EXAMPLES=TRUE -DSFML_BUILD_TEST_SUITE=TRUE -DCMAKE_BUILD_TYPE=Release -DBUILD_SHARED_LIBS=TRUE .. && cmake --build . -j8 -- install \
    && cmake -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++ -DCMAKE_CXX_FLAGS="-stdlib=libc++" -DSFML_BUILD_EXAMPLES=TRUE -DSFML_BUILD_TEST_SUITE=TRUE -DCMAKE_BUILD_TYPE=Release -DBUILD_SHARED_LIBS=FALSE .. && cmake --build . -j8 -- install

RUN echo "OK" > /verification-clang.txt

# Finalize Image
FROM final-layer

COPY --from=test-layer-gcc /verification-gcc.txt /verification-gcc.txt
COPY --from=test-layer-clang /verification-clang.txt /verification-clang.txt

RUN echo '#!/bin/sh \n\
set -e \n\
pkill -SIGTERM "fluxbox|Xvfb" || true \n\
daemonize /usr/bin/Xvfb $DISPLAY -screen 0 1920x1080x24 -ac +extension GLX +extension DPMS +render -noreset -s 1440 +bs -maxclients 256 +xinerama \n\
sleep 1 \n\
daemonize /usr/bin/fluxbox \n\
sleep 1 \n\
displayinfo=$(xdpyinfo -queryExtensions) \n\
echo "$displayinfo" | awk "/^name of display/,/^    significant bits in color specification/" \n\
' > /usr/local/bin/restartx && chmod +x /usr/local/bin/restartx

RUN echo '#!/bin/sh \n\
rm -rf $WORKERHOME \n\
mkdir -p $WORKERHOME \n\
buildbot-worker create-worker $WORKERHOME $BUILDMASTER:$BUILDMASTER_PORT $WORKERNAME $WORKERPASS \n\
echo $WORKERADMIN > $WORKERHOME/info/admin \n\
echo $WORKERDESCRIPTION > $WORKERHOME/info/host \n\
buildbot-worker start --nodaemon $WORKERHOME \n\
' > /start.sh && chmod +x /start.sh

ENV BUILDMASTER="masteraddress.invalid"
ENV BUILDMASTER_PORT=9989
ENV WORKERNAME="buildbot-worker-name"
ENV WORKERPASS="buildbot-worker-password"
ENV WORKERHOME=/home/buildbot-worker
ENV WORKERADMIN="binary1248 <binary1248@hotmail.com>"
ENV WORKERDESCRIPTION="binary1248's Debian Buildbot Worker"

ENV DISPLAY=":99"

CMD /start.sh
