FROM python:3.7.4-buster

WORKDIR /app
COPY ./setup.cfg ./setup.cfg
COPY ./setup.py ./setup.py
COPY ./requirements.txt ./requirements.txt

RUN mkdir src/ && pip install -r requirements.txt

COPY . .
RUN make install

ENTRYPOINT [ "python", "-m", "ixu" ]

CMD [ "server", "up" ]
