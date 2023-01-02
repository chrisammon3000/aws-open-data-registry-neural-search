# create a python 3.11 dockerfile for AWS fargate
FROM python:3.11.0a5-slim-buster

# install the requirements: pip, git
RUN apt-get update && apt-get install -y \
    git \
    python3-pip

ENV REPO_URL=""
ENV TARGET_DATA_DIR=""
ENV WEAVIATE_ENDPOINT=""

WORKDIR /opt/app

COPY . .

# install the requirements
RUN pip3 install -r requirements.txt

# run the app
CMD [ "python3", "src/app.py" ]