FROM debian:stable-slim AS final-layer

ARG COVERITY_TOKEN
ARG SONAR_TOKEN

RUN DEBIAN_FRONTEND=noninteractive \
    ln -fs /usr/share/zoneinfo/Europe/Berlin /etc/localtime \
    && apt-get update && apt-get install --no-install-recommends -y \
    tzdata \
    curl \
    wget \
    zip \
    unzip \
    git \
    file \
    ninja-build \
    build-essential \
    libmbedtls-dev \
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
    xvfb \
    fluxbox \
    novnc \
    && dpkg-reconfigure --frontend noninteractive tzdata \
    && apt-get autoremove -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# CMake
RUN wget https://github.com/Kitware/CMake/releases/download/v3.31.8/cmake-3.31.8.tar.gz \
    && tar xzf cmake-3.31.8.tar.gz \
    && cd cmake-3.31.8 \
    && ./bootstrap --parallel=$(nproc) \
    && make -j $(nproc) install \
    && cmake --version \
    && cd .. \
    && rm -rf cmake-3.31.8*

# pipx
RUN rm /usr/lib/python3.*/EXTERNALLY-MANAGED \
    && python3 -m pip install pipx \
    && rm -rf ~/.cache

ENV PATH="$PATH:/root/.local/bin"

# Buildbot Worker
RUN pipx install 'buildbot-worker' \
    && rm -rf ~/.cache

ENV COVERITY_TOKEN=${COVERITY_TOKEN:-invalid}

# Coverity
RUN rm -rf /usr/local/share/cov-analysis \
    && wget https://scan.coverity.com/download/linux64 --post-data "token=$COVERITY_TOKEN&project=SFML%2FSFML" -O coverity_tool.tgz \
    && tar xzf coverity_tool.tgz \
    && mv cov-analysis-* /usr/local/share/cov-analysis \
    && rm -rf coverity_tool.tgz \
    && rm -rf /usr/local/share/sonar

ENV SONAR_TOKEN=${SONAR_TOKEN:-invalid}
ENV SONAR_SCANNER_VERSION="6.2.0.4584-linux-x64"
ENV SONAR_SCANNER_OPTS="-server"

# Sonar
RUN curl --create-dirs -sSLo sonar-scanner.zip https://binaries.sonarsource.com/Distribution/sonar-scanner-cli/sonar-scanner-cli-$SONAR_SCANNER_VERSION.zip \
    && unzip -o sonar-scanner.zip -d /usr/local/share/sonar/ \
    && mv /usr/local/share/sonar/* /usr/local/share/sonar/sonar-scanner-linux \
    && rm -rf sonar-scanner.zip \
    && curl --create-dirs -sSLo build-wrapper-linux-x86.zip https://sonarcloud.io/static/cpp/build-wrapper-linux-x86.zip \
    && unzip -o build-wrapper-linux-x86.zip -d /usr/local/share/sonar/ \
    && rm -rf build-wrapper-linux-x86.zip

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
fluxbox > /dev/null 2>&1 & \n\
x11vnc -display $DISPLAY -viewonly -forever -shared -bg -nopw -localhost -quiet \n\
websockify -D --web=/usr/share/novnc/ 8081 localhost:5900 \n\
rm -rf $WORKERHOME \n\
mkdir -p $WORKERHOME \n\
 \n\
buildbot-worker create-worker $WORKERHOME $BUILDMASTER:$BUILDMASTER_PORT $WORKERNAME $WORKERPASS \n\
echo $WORKERADMIN > $WORKERHOME/info/admin \n\
echo $WORKERDESCRIPTION > $WORKERHOME/info/host \n\
 \n\
buildbot-worker start --nodaemon $WORKERHOME \n\
' > /start.sh \
    && chmod +x /start.sh

ENV BUILDMASTER="masteraddress.invalid"
ENV BUILDMASTER_PORT=9989
ENV WORKERNAME="buildbot-worker-name"
ENV WORKERPASS="buildbot-worker-password"
ENV WORKERHOME=/home/buildbot-worker
ENV WORKERADMIN="Your Name Here <admin@youraddress.invalid>"
ENV WORKERDESCRIPTION="Please put a description of this build host here"

ENV PATH "$PATH:/usr/local/share/cov-analysis/bin:/usr/local/share/sonar/sonar-scanner-linux/bin:/usr/local/share/sonar/build-wrapper-linux-x86"
ENV DISPLAY=":99"

CMD /start.sh
