FROM python:3

ENV HOME /opt/app
WORKDIR $HOME

ADD . $HOME

RUN \
  pip install -r requirements.txt

CMD python3 main.py
