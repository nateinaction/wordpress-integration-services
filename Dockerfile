FROM python

# install dependencies
RUN set -xe; \
    pip install \
    cryptography \
    flake8 \
    pyjwt \
    requests \
    semver

# copy the project files into place
COPY .gitconfig /root/
COPY .flake8 .
COPY src /app

# lint and test
RUN set -xe; \
    flake8 /app; \
    python3 -m unittest discover /app/update_develop; \
	python3 -m unittest discover /app/merge_master

WORKDIR /workspace
