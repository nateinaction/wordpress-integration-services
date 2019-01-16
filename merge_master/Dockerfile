FROM python

RUN pip install \
    cryptography \
    flake8 \
    pyjwt \
    requests \
    semver

COPY .gitconfig /root/
COPY main.py /
ENTRYPOINT [ "/main.py" ]
WORKDIR /workspace
