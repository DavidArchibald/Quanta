FROM python:3.6

ADD /src/requirements.txt /app/src/requirements.txt
RUN pip install --trusted-host pypi.python.org -r /app/src/requirements.txt

ADD /src/secrets/config.yaml /app/src/secrets/config.yaml
ADD /src /app/src

RUN sed -i 's/localhost/host.docker.internal/g' /app/src/secrets/config.yaml
ENV PYTHONPATH /app

CMD ["python", "-m", "src.main"]
