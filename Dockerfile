# Built based on concepts here: 
# https://blog.realkinetic.com/building-minimal-docker-containers-for-python-applications-37d0272c52f3
FROM python:3.7-alpine 
# Install Pipenv: from https://github.com/VaultVulp/pipenv-alpine/blob/master/Dockerfile
RUN apk update \
        && apk add --no-cache git openssh-client \
        && pip install pipenv \
        && addgroup -S -g 1001 app \
        && adduser -S -D -h /app -u 1001 -G app app
# Install dependencies first for fast builds when dependencies are unchanged
COPY Pipfile* /
RUN pipenv install --dev
COPY *.py /app/
COPY *.csv /app/
COPY *.db /app/
COPY test/ /app/
WORKDIR /app
CMD pipenv run python cohort_analysis.py
