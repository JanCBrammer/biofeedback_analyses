# build Docker image with `docker build -t image-name .` in directory containing the `biofeedback_analyses` repository

# run Docker image (i.e., instantiate Docker container) with `docker run --mount type=bind,source="$(pwd)",target=/app/data image-name` in directory containing the `raw` data folder

FROM python:3.8.10-slim

# get all files required for installing analysis pipeline
RUN mkdir /app
WORKDIR /app
COPY /biofeedback_analyses ./biofeedback_analyses
COPY pyproject.toml .
COPY poetry.lock .

# install analysis pipeline (important not to have poetry create a virtual environment since we're already isolated in a Docker container)
RUN pip3 install "poetry==1.1.6"
RUN poetry config virtualenvs.create false
RUN poetry install

# create, and change to the directory where the data directory needs to be mounted when running the container:
# `docker run --mount type=bind,source="$(pwd)",target=/app/data image-name`
WORKDIR data

# run analysis pipeline by executing entry point
CMD ["plot_figures"]