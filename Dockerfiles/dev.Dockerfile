# build an image from this Dockerfile with:
#     docker build -t ricardogsilva/pycsw_next_dev ..
#
# then run it with:
#     docker run -ti --name pycsw_next_dev -p 8888:8888 -v /home/ricardo/dev/pycsw:/opt/pycsw:ro ricardogsilva/pycsw_next_dev
FROM ricardogsilva/pycsw_next

WORKDIR /opt/pycsw

copy . .

USER root

# Add Tini (a small init system to control jupyter-notebook)
ENV TINI_VERSION v0.10.0
ADD https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini /tini
RUN chmod +x /tini
ENTRYPOINT ["/tini", "--"]
CMD ["jupyter-notebook", "--no-browser", "--ip", "0.0.0.0", "--notebook-dir", "/tmp"]

# Adding additional dev packages
RUN pip install --requirement requirements/dev.txt && \
    mkdir /home/user && chown -R user:user /home/user

EXPOSE 8888

USER user

# TODO
# * mount a local dir with ipython notebooks as well as the source code
#   for pycsw. This will allow persisting notebooks
