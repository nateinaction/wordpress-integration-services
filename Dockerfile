FROM python

RUN pip install \
    cryptography \
    flake8 \
    pyjwt \
    requests \
    semver

COPY .gitconfig /root/
COPY update_develop/main.py /update_develop/main.py
COPY merge_master/main.py /merge_master/main.py
WORKDIR /workspace
