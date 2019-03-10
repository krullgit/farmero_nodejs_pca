FROM debian:jessie as builder

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8
RUN apt-get update && \
  apt-get install -yq --no-install-recommends \
    curl \
    bzip2 \
    ca-certificates

ENV MINICONDA_VERSION 4.5.4
ENV PATH=/opt/conda/bin:$PATH
RUN cd /tmp && \
    curl -sSL https://repo.continuum.io/miniconda/Miniconda3-${MINICONDA_VERSION}-Linux-x86_64.sh -o /tmp/miniconda.sh && \
    echo "a946ea1d0c4a642ddf0c3a26a18bb16d *miniconda.sh" | md5sum -c - && \
    /bin/bash miniconda.sh -f -b -p /opt/conda && \
    rm miniconda.sh && \
    /opt/conda/bin/conda config --system --prepend channels conda-forge && \
    /opt/conda/bin/conda config --system --set auto_update_conda false && \
    /opt/conda/bin/conda config --system --set show_channel_urls true && \
    /opt/conda/bin/conda install --quiet --yes conda="${MINICONDA_VERSION%.*}.*" && \
    /opt/conda/bin/conda update --all --quiet --yes && \
    conda clean -tipsy

ADD python_envs/environment_p2.yml /tmp/environment_p2.yml
RUN conda env create -f /tmp/environment_p2.yml

ADD python_envs/environment_p3.yml /tmp/environment_p3.yml
RUN conda env create -f /tmp/environment_p3.yml

RUN conda install -c conda-forge earthengine-api

#RUN earthengine authenticate --quiet

#RUN earthengine authenticate --authorization-code=4/CAEb3-Y0358CvZbJFzw8cYj01PYGdql4PBvA8G8R-Qj72g7vUzB3oCY

#RUN python -c "import ee; ee.Initialize()"

RUN apt-get install --reinstall -y libgtk2.0-0

RUN conda install nodejs git

WORKDIR /farmero_nodejs_pca

#COPY . /farmero_nodejs_pca/

RUN npm install .


EXPOSE 3000

CMD [ "npm", "start"]