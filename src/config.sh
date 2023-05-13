#!/bin/bash -xe

# Mounting EBS to m6i
DEBIAN_FRONTEND=noninteractive 
apt-get update -y
# Ubuntu 20 Bug prevents upgrading docker.io package noninteractively
# apt-get upgrade -y
# systemctl restart docker
mkfs -t ext4 /dev/nvme1n1
mkdir /data
mount /dev/nvme1n1 /data
cp /etc/fstab /etc/fstab.bak
echo '/dev/nvme1n1 /data ext4 defaults,nofail 0 0' | sudo tee -a /etc/fstab
mount -a
# Install Docker Compose and run
# https://www.cherryservers.com/blog/how-to-install-and-use-docker-compose-on-ubuntu-20-04
apt update -y
apt install ca-certificates curl gnupg lsb-release -y
mkdir /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
    $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list
apt-get update -y
apt install docker-ce docker-ce-cli containerd.io docker-compose-plugin -y
usermod -a -G docker ubuntu
curl -o /home/ubuntu/docker-compose.yml "https://configuration.weaviate.io/v2/docker-compose/docker-compose.yml?generative_cohere=false&gpu_support=false&media_type=text&modules=modules&ner_module=false&qna_module=false&ref2vec_centroid=false&runtime=docker-compose&spellcheck_module=false&sum_module=false&text_module=text2vec-transformers&transformers_model=sentence-transformers-multi-qa-MiniLM-L6-cos-v1&weaviate_version=v1.19.0"
sleep 1
# awk '/^  weaviate:$/ {print; getline; print "    volumes:\n      - /data/weaviate:/var/lib/weaviate"; print "    command:"; next} 1' /home/ubuntu/docker-compose.yml > /home/ubuntu/docker-compose-new.yml
awk '/^  weaviate:$/ {print; print "    restart: always"; print "    volumes:"; print "      - /data/weaviate:/var/lib/weaviate"; next} /^  t2v-transformers:$/ {print; print "    restart: always"; next} 1' /home/ubuntu/docker-compose.yml > /home/ubuntu/docker-compose-new.yml
sed -i "s/CLUSTER_HOSTNAME: 'node1'/&\n      AUTOSCHEMA_ENABLED: 'false'/" /home/ubuntu/docker-compose-new.yml
mv /home/ubuntu/docker-compose-new.yml /home/ubuntu/docker-compose.yml
cd /home/ubuntu && docker compose up -d