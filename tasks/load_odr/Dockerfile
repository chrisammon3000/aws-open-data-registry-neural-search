FROM --platform=linux/amd64 python:3.10-slim-buster

# install the requirements: pip, git
RUN apt-get update && apt-get install -y \
    git \
    python3-pip

ENV REPO_URL=""
ENV TARGET_DATA_DIR=""
ENV WEAVIATE_ENDPOINT_SSM_PARAM=""

WORKDIR /opt/app

COPY . .

# install the requirements
RUN pip3 install -r requirements.txt

# run the app
CMD [ "python3", "app.py" ]