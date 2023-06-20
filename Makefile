# Adds .env variables to the environment, used for secrets
include .env
export

# Deployment variables
export ROOT_DIR ?= $(shell pwd)
export ORGANIZATION ?= $(shell jq -r '.tags.org' ${ROOT_DIR}/config.json)
export APP_NAME ?= $(shell jq -r '.tags.app' ${ROOT_DIR}/config.json)
export IAM_USER ?= $(shell aws sts get-caller-identity | jq -r '.Arn' | cut -d'/' -f 2)

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

app: venv
	$(MAKE) deploy
	@echo "Loading data into Weaviate..."
	$(MAKE) job.run
	$(MAKE) job.wait
	@echo "Starting Streamlit server..."
	$(MAKE) streamlit.run

venv:
	@echo "Creating virtual environment..."
	@python3.10 -m venv .venv
	@source .venv/bin/activate && \
	pip install -r requirements.txt

 # Deploy services
deploy: check-env
	$(info [*] Deploying ${APP_NAME} to ${CDK_DEFAULT_ACCOUNT})
	@echo "Creating EC2 key pair..."
	$(MAKE) create-key-pair
	@echo "Deploying CDK stack..."
	@cdk deploy --require-approval never
	$(MAKE) weaviate.wait
	@echo "Creating Weaviate schema..."
	$(MAKE) weaviate.schema.create

destroy:
	$(info [*] Destroying ${APP_NAME} in ${CDK_DEFAULT_ACCOUNT})
	@cdk destroy
	@EC2_KEY_PAIR_NAME="$$(jq -r '.layers.vector_database.env.ssh_key_name' ${ROOT_DIR}/config.json)" && \
	aws ec2 delete-key-pair --key-name "$$EC2_KEY_PAIR_NAME" && \
	mv ${ROOT_DIR}/$$EC2_KEY_PAIR_NAME.pem ${ROOT_DIR}/deprecated-key-$$(date -u +'%Y-%m-%d-%H-%M').pem

create-key-pair: ##=> Checks if the key pair already exists and creates it if it does not
	@echo "$$(date -u +'%Y-%m-%d %H:%M:%S.%3N') - Checking for key pair $$EC2_KEY_PAIR_NAME" 2>&1 | tee -a $$CFN_LOG_PATH
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
	res=$$(aws batch submit-job \
		--job-name=$$job_name \
		--job-queue=$$job_queue_arn \
		--job-definition=$$job_definition_arn \
		--container-overrides command=$$cmd) && \
	echo && \
	echo "Job submitted:" && \
	echo $$res | jq -r && \
	echo $$res > job.json

job.status:
	@job_id=$$(jq -r '.jobId' job.json) && \
	res=$$(aws batch describe-jobs --jobs $$job_id) && \
	echo $$res | jq -r --arg jobId "$$job_id" '.jobs[] | select(.jobId==$$jobId) | "\(.status)"'

job.wait:
	@job_id=$$(jq -r '.jobId' job.json) && \
	timeout=300 && \
	counter=0 && \
	echo "Waiting for job to complete..." && \
	while true; do \
		job_status=$$(res=$$(aws batch describe-jobs --jobs $$job_id) && \
		echo $$res | jq -r --arg jobId "$$job_id" '.jobs[] | select(.jobId==$$jobId) | "\(.status)"'); \
		if [ "$$job_status" = "SUCCEEDED" ]; then \
			echo "Done"; \
			rm job.json; \
			break; \
		elif [ "$$job_status" = "FAILED" ]; then \
			echo "Job failed"; \
			exit 1; \
		else \
			printf '.' ; \
			sleep 1 ; \
			counter=$$((counter + 1)) ; \
			if [ $$counter -eq $$timeout ]; then \
				echo "Operation timed out!" ; \
				exit 1; \
			fi; \
		fi; \
	done 

weaviate.status:
	@instance_id=$$(aws ssm get-parameters --names "/${ORGANIZATION}/${APP_NAME}/InstanceId" | jq -r '.Parameters[0].Value') && \
	aws ec2 describe-instances | \
		jq --arg iid "$$instance_id" '.Reservations[].Instances[] | select(.InstanceId == $$iid) | {InstanceId, InstanceType, "Status": .State.Name, StateTransitionReason, ImageId}'

weaviate.start:
	@echo "Starting $${APP_NAME} server..."
	@instance_id=$$(aws ssm get-parameters --names "/${ORGANIZATION}/${APP_NAME}/InstanceId" | jq -r '.Parameters[0].Value') && \
	response=$$(aws ec2 start-instances --instance-ids $$instance_id) && \
	echo $$response | jq -r
	$(MAKE) weaviate.wait

weaviate.stop:
	@echo "Stopping $${APP_NAME} server..."
	@instance_id=$$(aws ssm get-parameters --names "/${ORGANIZATION}/${APP_NAME}/InstanceId" | jq -r '.Parameters[0].Value') && \
	response=$$(aws ec2 stop-instances --instance-ids $$instance_id) && \
	echo $$response | jq -r

weaviate.reboot:
	@echo "Rebooting $${APP_NAME} server..."
	@instance_id=$$(aws ssm get-parameters --names "/${ORGANIZATION}/${APP_NAME}/InstanceId" | jq -r '.Parameters[0].Value') && \
	response=$$(aws ec2 reboot-instances --instance-ids $$instance_id) && echo "$$response"
	$(MAKE) weaviate.wait

weaviate.wait:
	@endpoint=$$(aws ssm get-parameters \
		--names "/${ORGANIZATION}/${APP_NAME}/WeaviateEndpoint" | jq -r '.Parameters[0].Value') && \
	timeout=240 && \
	counter=0 && \
	echo "Waiting for response from Weaviate at $$endpoint..." && \
	until [ $$(curl -s -o /dev/null -w "%{http_code}" $$endpoint/v1) -eq 200 ] ; do \
		printf '.' ; \
		sleep 1 ; \
		counter=$$((counter + 1)) ; \
		[ $$counter -eq $$timeout ] && break || true ; \
	done && \
	[ $$counter -eq $$timeout ] && $$(echo "Operation timed out!" && exit 1) || echo "Ready"

weaviate.get.endpoint:
	@endpoint=$$(aws ssm get-parameters --names "/${ORGANIZATION}/${APP_NAME}/WeaviateEndpoint" | jq -r '.Parameters[0].Value') && \
	echo "$$endpoint"

weaviate.schema.create:
	@bash scripts/create_schema.sh

weaviate.schema.delete:
	@printf "Deleting the schema will remove all data. Do you wish to continue? [y/N] " && \
	read ans && [ $${ans:-N} = y ] && \
	bash scripts/delete_schema.sh

streamlit.run:
	@echo "Starting Streamlit server..."
	@source .venv/bin/activate && \
	streamlit run frontend/Open_Data_Registry.py

define HELP_MESSAGE

	Environment variables:

	CDK_DEFAULT_ACCOUNT: "${CDK_DEFAULT_ACCOUNT}":
		Description: AWS account ID for deployment

	CDK_DEFAULT_REGION: "${CDK_DEFAULT_REGION}":
		Description: AWS region for deployment

	ROOT_DIR: "${ROOT_DIR}":
		Description: Project directory containing the full source code

	ORGANIZATION: "${ORGANIZATION}":
		Description: Organization name, declared in `config.json`

	APP_NAME: "${APP_NAME}":
		Description: Application name, declared in `config.json`

	IAM_USER: "${IAM_USER}":
		Description: IAM user name for job name
		
	Common usage:

	...::: Deploy all CloudFormation based services :::...
	$ make deploy

	...::: Delete all CloudFormation based services and data :::...
	$ make delete

endef
