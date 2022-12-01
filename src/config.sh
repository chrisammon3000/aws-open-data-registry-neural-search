#!/bin/bash -xe

# https://www.cyberciti.biz/faq/how-to-install-docker-on-amazon-linux-2/
yum install git docker -y
usermod -a -G docker ec2-user
id ec2-user
newgrp docker
pip3 install docker-compose
sudo systemctl enable docker.service
sudo systemctl start docker.service
curl -o docker-compose.yml "https://configuration.semi.technology/v2/docker-compose/docker-compose.yml?modules=standalone&runtime=docker-compose&weaviate_version=v1.16.5"