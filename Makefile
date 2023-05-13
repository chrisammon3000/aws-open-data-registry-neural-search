##########################
# Bootstrapping variables
##########################

# Adds .env variables to the environment, used for secrets
include .env
export

# Deployment variables
export ROOT_DIR ?= $(shell pwd)
export ORGANIZATION ?= $(shell jq -r '.tags.org' ${ROOT_DIR}/config.json)
export APP_NAME ?= $(shell jq -r '.tags.app' ${ROOT_DIR}/config.json)


# AWS resources
export CDK_DEFAULT_ACCOUNT ?= $(shell aws sts get-caller-identity --query Account --output text || exit 1)

target:
	$(info ${HELP_MESSAGE})
	@exit 0

check-env:
ifndef CDK_DEFAULT_ACCOUNT
$(error CDK_DEFAULT_ACCOUNT is not set. Please select an AWS profile to use.)
endif
ifndef CDK_DEFAULT_REGION
$(error CDK_DEFAULT_REGION is not set. Please select an AWS profile to use.)
endif
	@echo "Found environment variables"


key:
	@EC2_KEY_PAIR_NAME="$$(jq -r '.layers.vector_database.env.ssh_key_name' ${ROOT_DIR}/config.json)" && \
	key_pair="$$(aws ec2 describe-key-pairs --key-name $$EC2_KEY_PAIR_NAME | jq -r --arg KEY_PAIR "$$EC2_KEY_PAIR_NAME" '.KeyPairs[] | select(.KeyName == $$KEY_PAIR).KeyName')" && \
	echo $$EC2_KEY_PAIR_NAME && echo $$key_pair

 # Deploy services
deploy: check-env
	$(info [*] Deploying to ${CDK_DEFAULT_ACCOUNT}.)
	$(MAKE) create-key-pair
	@cdk deploy

create-key-pair: ##=> Checks if the key pair already exists and creates it if it does not
	@echo "$$(gdate -u +'%Y-%m-%d %H:%M:%S.%3N') - Checking for key pair $$EC2_KEY_PAIR_NAME" 2>&1 | tee -a $$CFN_LOG_PATH
	@EC2_KEY_PAIR_NAME="$$(jq -r '.layers.vector_database.env.ssh_key_name' ${ROOT_DIR}/config.json)" && \
	key_pair="$$(aws ec2 describe-key-pairs --key-name $$EC2_KEY_PAIR_NAME | jq -r --arg KEY_PAIR "$$EC2_KEY_PAIR_NAME" '.KeyPairs[] | select(.KeyName == $$KEY_PAIR).KeyName')" && \
	[ "$$key_pair" ] && echo "Key pair found: $$key_pair" && exit 0 || echo "No key pair found..." && \
	echo "Creating EC2 key pair \"$$EC2_KEY_PAIR_NAME\"" && \
	aws ec2 create-key-pair --key-name $$EC2_KEY_PAIR_NAME | jq -r '.KeyMaterial' > ${ROOT_DIR}/$$EC2_KEY_PAIR_NAME.pem

define HELP_MESSAGE

	Environment variables:

	CDK_DEFAULT_ACCOUNT: "${CDK_DEFAULT_ACCOUNT}":
		Description: AWS account ID for deployment

	CDK_DEFAULT_REGION: "${CDK_DEFAULT_REGION}":
		Description: AWS region for deployment

	ROOT_DIR: "${ROOT_DIR}":
		Description: Project directory containing the full source code
		
	Common usage:

	...::: Deploy all CloudFormation based services :::...
	$ make deploy

	...::: Delete all CloudFormation based services and data :::...
	$ make delete

endef
