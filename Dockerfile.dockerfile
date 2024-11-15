FROM python:3.11.2-buster
ENV DEBIAN_FRONTEND='noninteractive'
RUN apt-get update && apt install -y curl
RUN curl -sSL https://install.python-poetry.org | python
ENV PATH="${PATH}:/root/.local/bin"
RUN poetry config virtualenvs.in-project false
WORKDIR ../app
COPY . .
RUN poetry install
EXPOSE 8000

