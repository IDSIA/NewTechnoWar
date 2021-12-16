FROM python:3.7-slim-buster AS base
FROM python:3.7 as builder

# build stage
RUN python -m venv /opt/venv

ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.linux.cpu.txt /requirements.txt

RUN pip install -r /requirements.txt

# deploy stage
FROM base

COPY --from=builder /opt/venv /opt/venv

RUN useradd --create-home ntw

COPY ./ /home/ntw/code/

RUN chown -R ntw:ntw /home/ntw/*

WORKDIR /home/ntw/code/
#USER obpa

ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONENV="/home/ntw/code/:$PYTHONENV"

CMD ["gunicorn", "-b", "0.0.0.0:5000", "web.wsgi:application"]
