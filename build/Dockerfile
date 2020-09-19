FROM google/cloud-sdk:307.0.0

# Install make
RUN set -ex; \
    apt-get update; \
    apt-get install -y make; \
    rm -rf /var/lib/apt/lists/*

# Install docker
ENV DOCKER_VER 19.03.9
RUN set -ex; \
    curl -fsSL https://download.docker.com/linux/static/stable/x86_64/docker-${DOCKER_VER}.tgz -o docker.tgz; \
    tar -xvf docker.tgz; \
    mv docker/* /usr/local/bin/; \
    rm -rf docker*

# Install kustomize
ENV KUSTOMIZE_VER 3.8.2
RUN set -ex; \
    curl -fsSL "https://github.com/kubernetes-sigs/kustomize/releases/download/kustomize/v${KUSTOMIZE_VER}/kustomize_v${KUSTOMIZE_VER}_linux_amd64.tar.gz" -o kustomize.tar.gz; \
    tar -C /usr/local/bin/ -xzf kustomize.tar.gz; \
    rm kustomize.tar.gz

WORKDIR /workspace
ENTRYPOINT ["/usr/bin/make"]
