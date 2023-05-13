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
export IAM_USER ?= $(shell aws sts get-caller-identity | jq -r '.Arn' | cut -d'/' -f 2)

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

job.run:
	@cmd="[\"python3\",\"app.py\"]" && \
	for param in $$params ; do \
		cmd=$$(echo $$cmd | jq -r --arg p "\"$$param\"" '. += [$$p] | tostring') ; \
	done && \
	cmd=$$(echo "$$cmd" | jq -r '. | join(",")') && \
	job_name="${IAM_USER}-$$(date +%y%m%d-%s)" && \
	job_queue_arn=$$(aws ssm get-parameters \
		--names "/${ORGANIZATION}/${APP_NAME}/AmzOdrDataIngestionJobQueueArn" \
	| jq -r '.Parameters[0].Value') && \
	job_definition_arn=$$(aws ssm get-parameters \
		--names "/${ORGANIZATION}/${APP_NAME}/AmzOdrDataIngestionJobDefArn" \
	| jq -r '.Parameters[0].Value') && \
	printf "\n***************************************************************************" && \
	printf "\n\nPlease confirm the command for the job you are submitting:\n\n" && \
	echo \"$$(echo $$cmd | sed 's/,/ /g' | sed 's/\"//g')\" && \
	printf "\n***************************************************************************" && \
	printf "\n\nDo you wish to continue? [y/N] " && read ans && [ $${ans:-N} = y ] && \
	res=$$(aws batch submit-job \
		--job-name=$$job_name \
		--job-queue=$$job_queue_arn \
		--job-definition=$$job_definition_arn \
		--container-overrides command=$$cmd) && \
	echo && \
	echo "Job submitted:" && \
	echo $$res | jq -r

job.status: #==> job.status job_id="<jobId>"
	@[[ -z "$$job_id" ]] && echo "no job ID found" || \
	res=$$(aws batch describe-jobs --jobs $$job_id) && \
	echo $$res | jq -r --arg jobId "$$job_id" '.jobs[] | select(.jobId==$$jobId) | "\(.status)"'

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
