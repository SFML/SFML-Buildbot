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
RUN python3 -m pip install pipx \
    && rm -rf ~/.cache

ENV PATH="$PATH:/root/.local/bin"

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

# Finalize Image
FROM final-layer

COPY --from=test-layer-gcc /verification-gcc.txt /verification-gcc.txt

RUN echo ' \n\
rm -rf /tmp/.X11-unix/ \n\
rm -rf /tmp/.X99-lock \n\
Xvfb $DISPLAY -screen 0 1920x1080x24 & \n\
rm -rf /usr/local/share/cov-analysis \n\
wget https://scan.coverity.com/download/linux64 --post-data "token=$COVERITY_TOKEN&project=SFML%2FSFML" -O coverity_tool.tgz || true \n\
tar xzf coverity_tool.tgz || true \n\
mv cov-analysis-* /usr/local/share/cov-analysis || true \n\
rm -rf coverity_tool.tgz \n\
rm -rf /usr/local/share/sonar \n\
curl --create-dirs -sSLo sonar-scanner.zip https://binaries.sonarsource.com/Distribution/sonar-scanner-cli/sonar-scanner-cli-$SONAR_SCANNER_VERSION-linux.zip \n\
unzip -o sonar-scanner.zip -d /usr/local/share/sonar/ \n\
mv /usr/local/share/sonar/* /usr/local/share/sonar/sonar-scanner-linux \n\
rm -rf sonar-scanner.zip \n\
curl --create-dirs -sSLo build-wrapper-linux-x86.zip https://sonarcloud.io/static/cpp/build-wrapper-linux-x86.zip \n\
unzip -o build-wrapper-linux-x86.zip -d /usr/local/share/sonar/ \n\
rm -rf build-wrapper-linux-x86.zip \n\
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

ENV PATH "$PATH:/usr/local/share/cov-analysis/bin:/usr/local/share/sonar/sonar-scanner-linux/bin:/usr/local/share/sonar/build-wrapper-linux-x86"
ENV BUILDBOT_HOME=/home/buildbot-worker
ENV BUILDBOT_ADMIN="Your Name Here <admin@youraddress.invalid>"
ENV BUILDBOT_DESCRIPTION="Please put a description of this build host here"
ENV BUILDBOT_MASTER_HOST="masteraddress.invalid"
ENV BUILDBOT_MASTER_PORT=9989
ENV BUILDBOT_WORKER_NAME="buildbot-worker-name"
ENV BUILDBOT_WORKER_PASSWORD="buildbot-worker-password"
ENV COVERITY_TOKEN="invalid"
ENV SONAR_SCANNER_VERSION="4.7.0.2747"
ENV SONAR_SCANNER_OPTS="-server"
ENV SONAR_TOKEN="invalid"
ENV DISPLAY=":99"

CMD /start.sh
