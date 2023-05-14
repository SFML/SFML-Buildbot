FROM debian:unstable-slim AS final-layer

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
    libfreetype6-dev \
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
    xvfb \
    fluxbox \
    novnc \
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

RUN echo ' \n\
Xvfb $DISPLAY -screen 0 1920x1080x24 & \n\
fluxbox > /dev/null 2>&1 & \n\
x11vnc -display $DISPLAY -viewonly -forever -shared -bg -nopw -localhost -quiet \n\
websockify -D --web=/usr/share/novnc/ 8081 localhost:5900 \n\
rm -rf $BUILDBOT_HOME \n\
mkdir -p $BUILDBOT_HOME \n\
 \n\
buildbot-worker create-worker $BUILDBOT_HOME $BUILDBOT_MASTER_HOST:$BUILDBOT_MASTER_PORT $BUILDBOT_WORKER_NAME $BUILDBOT_WORKER_PASSWORD \n\
echo $BUILDBOT_ADMIN > $BUILDBOT_HOME/info/admin \n\
echo $BUILDBOT_DESCRIPTION > $BUILDBOT_HOME/info/host \n\
 \n\
buildbot-worker start --nodaemon $BUILDBOT_HOME \n\
' > /start.sh \
    && chmod +x /start.sh

ENV BUILDBOT_HOME=/home/buildbot-worker
ENV BUILDBOT_ADMIN="Your Name Here <admin@youraddress.invalid>"
ENV BUILDBOT_DESCRIPTION="Please put a description of this build host here"
ENV BUILDBOT_MASTER_HOST="masteraddress.invalid"
ENV BUILDBOT_MASTER_PORT=9989
ENV BUILDBOT_WORKER_NAME="buildbot-worker-name"
ENV BUILDBOT_WORKER_PASSWORD="buildbot-worker-password"
ENV DISPLAY=":99"

CMD /start.sh
