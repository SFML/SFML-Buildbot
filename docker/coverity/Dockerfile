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
    cmake \
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
    python3-pip \
    python3-dev \
    && dpkg-reconfigure --frontend noninteractive tzdata \
    && apt-get autoremove -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Buildbot Worker
RUN pip3 install 'buildbot-worker' \
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
rm -rf /usr/local/share/cov-analysis \n\
wget https://scan.coverity.com/download/linux64 --post-data "token=$COVERITY_TOKEN&project=SFML%2FSFML" -O coverity_tool.tgz || true \n\
tar xzf coverity_tool.tgz || true \n\
mv cov-analysis-* /usr/local/share/cov-analysis || true \n\
rm -rf coverity_tool.tgz \n\
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

ENV PATH "$PATH:/usr/local/share/cov-analysis/bin"
ENV BUILDBOT_HOME=/home/buildbot-worker
ENV BUILDBOT_ADMIN="Your Name Here <admin@youraddress.invalid>"
ENV BUILDBOT_DESCRIPTION="Please put a description of this build host here"
ENV BUILDBOT_MASTER_HOST="masteraddress.invalid"
ENV BUILDBOT_MASTER_PORT=9989
ENV BUILDBOT_WORKER_NAME="buildbot-worker-name"
ENV BUILDBOT_WORKER_PASSWORD="buildbot-worker-password"
ENV COVERITY_TOKEN="invalid"

CMD /start.sh
