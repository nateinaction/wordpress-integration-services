FROM docker:19.03

# Add make
RUN apk add --no-cache curl make

# add kubectl
RUN set -ex; \
    curl -LO "https://storage.googleapis.com/kubernetes-release/release/$(curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt)/bin/linux/amd64/kubectl"; \
    chmod +x kubectl; \
    mv kubectl /usr/local/bin/kubectl

WORKDIR /workspace
ENTRYPOINT ["/usr/bin/make"]
