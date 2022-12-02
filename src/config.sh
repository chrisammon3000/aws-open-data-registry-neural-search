#!/bin/bash -xe

# https://www.cyberciti.biz/faq/how-to-install-docker-on-amazon-linux-2/
yum install git docker -y
usermod -a -G docker ec2-user
id ec2-user
newgrp docker
pip3 install docker-compose
sudo systemctl enable docker.service
sudo systemctl start docker.service
curl -o docker-compose.yml "https://configuration.semi.technology/v2/docker-compose/docker-compose.yml?gpu_support=false&media_type=text&modules=modules&ner_module=false&qna_module=false&ref2vec_centroid=false&runtime=docker-compose&spellcheck_module=false&sum_module=false&text_module=text2vec-transformers&transformers_model=sentence-transformers-multi-qa-MiniLM-L6-cos-v1&weaviate_version=v1.16.5"
docker-compose up -d
# create schema using curl