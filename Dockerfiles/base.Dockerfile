# build an image from this Dockerfile with:
#
#     docker build -t ricardogsilva/pycsw_next ..

FROM ubuntu:16.04
MAINTAINER Ricardo Silva <ricardo.garcia.silva@gmail.com>

WORKDIR /opt/pycsw
COPY . .

RUN apt-get update && apt-get install --yes \
        libxml2 \
        libxml2-dev \
        libxslt1.1 \
        libxslt1-dev \
        python3 \
        python3-dev \
        python3-pip \
        wget \
        zlib1g \
        zlib1g-dev && \
    # pip and python dependencies
    ln -s /usr/bin/python3 /usr/bin/python && \
    ln -s /usr/bin/pip3 /usr/bin/pip && \
    pip install --upgrade pip && \
    pip install --requirement requirements/base.txt && \
    # reinstalling PyXB with OGC bindings
    mkdir build && \
    cd build && \
    pip download pyxb==1.2.4 && \
    tar -zxvf PyXB-1.2.4.tar.gz  && \
    cd PyXB-1.2.4&& \
    export PYXB_ROOT=$(pwd) && \
    maintainer/genbundles @ && \
    pyxb/bundles/opengis/scripts/genbind && \
    pip install --upgrade . && \
    cd ../.. && \
    rm -rf build && \
    # removing unneeded stuff
    apt-get purge --yes \
        libxml2-dev \
        libxslt1-dev \
        python3-dev \
        wget \
        zlib1g-dev && \
    apt-get autoremove --yes && \
    apt-get clean

# installing pycsw in editable mode
RUN pip install --editable .

RUN useradd --user-group user
USER user

# todo:

# * Base image becoming alpine, changing apt-get to apk and etc
# * Perhaps building one image for QA and another for production, with
#   different requirements
# * Add entrypoint for running pycsw on the prod image and another for running
#   tests in the test image
# * test the mounting of a local directory as a way to work on the code

