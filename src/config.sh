#!/bin/bash -xe

# https://www.cyberciti.biz/faq/how-to-install-docker-on-amazon-linux-2/
yum update -y
yum install git docker -y
usermod -a -G docker ec2-user
usermod -a -G docker ssm-user
id ec2-user
newgrp docker
pip3 install docker-compose
sudo systemctl enable docker.service
sudo systemctl start docker.service
git clone https://github.com/abk7777/aws-open-data-registry-neural-search.git /opt/app
cd /opt/app
docker-compose up -d