# aws-open-data-registry-neural-search
Semantic search of AWS Open Data Registry datasets using Weaviate.

## Table of Contents
- [aws-open-data-registry-neural-search](#aws-open-data-registry-neural-search)
  - [Table of Contents](#table-of-contents)
  - [Project Structure](#project-structure)
  - [Description](#description)
  - [Quickstart](#quickstart)
  - [Installation](#installation)
    - [Prerequisites](#prerequisites)
    - [Environment Variables](#environment-variables)
    - [CDK Application Configuration](#cdk-application-configuration)
    - [AWS Credentials](#aws-credentials)
    - [Jupyter Notebook Setup](#jupyter-notebook-setup)
    - [Python Development](#python-development)
  - [Usage](#usage)
    - [Makefile Usage](#makefile-usage)
    - [Docker](#docker)
    - [AWS Deployment](#aws-deployment)
    - [CDK Commands](#cdk-commands)
  - [Troubleshooting](#troubleshooting)
  - [References \& Links](#references--links)
  - [Authors](#authors)

## Project Structure
```bash
.
├── Makefile
├── README.md
├── (aws-open-data-registry-neural-search-key-pair.pem)
├── bin
├── cdk.context.json
├── cdk.json
├── config.json
├── frontend
├── jest.config.js
├── lib
├── notebooks
├── package.json
├── requirements.txt
├── scripts
│   └── delete_schema.sh
├── src
│   └── config.sh
├── tasks
│   └── load_odr
├── test
└── tsconfig.json
```

## Description
Deploy and load a Weaviate instance with [AWS Open Data Registry](https://registry.opendata.aws/) datasets. Find datasets, tutorials, publications and tools & applications using semantic search and natural language processing queries using the Streamlit app.

<!-- TODO ### Architecture -->

## Quickstart
1. Configure your AWS credentials.
2. Add environment variables to `.env`.
3. Update `config.json` if desired.
4. Run `npm install` to install TypeScript dependencies.
5. Run `make deploy` to deploy the app.
6. Run `make job.run` to load the database.
<!-- TODO 7. Start the Streamlit app to search records. -->

## Installation
Follow the steps to configure the deployment environment.

### Prerequisites
* Docker
* Nodejs >= 18.0.0
* TypeScript >= 4.4.3
* AWS CDK >= 2.53.0
* Python 3.10
* AWSCLI
* jq

### Environment Variables
Sensitive environment variables containing secrets like passwords and API keys must be exported to the environment first.

Create a `.env` file in the project root.
```bash
CDK_DEFAULT_ACCOUNT=<account_id>
CDK_DEFAULT_REGION=<region>
WEAVIATE_ENDPOINT=<hostname>
```

***Important:*** *Always use a `.env` file or AWS SSM Parameter Store or Secrets Manager for sensitive variables like credentials and API keys. Never hard-code them, including when developing. AWS will quarantine an account if any credentials get accidentally exposed and this will cause problems.*

***Make sure that `.env` is listed in `.gitignore`***

### CDK Application Configuration
The CDK application configuration is stored in `config.json`. This file contains values for the database layer, the data ingestion layer, and tags. You can update the tags and SSH IP to your own values before deploying.
```json
{
    "layers": {
        "data_ingestion": {
            "env": {
                "repo_url": "https://github.com/awslabs/open-data-registry",
                "target_data_dir": "datasets"
            }
        },
        "vector_database": {
            "env": {
                "ssh_cidr": "0.0.0.0/0", // Update to your IP
                "ssh_key_name": "aws-open-data-registry-neural-search-key-pair"
            }
        }
    },
    "tags": {
        "org": "my-organization", // Update to your organization
        "app": "aws-open-data-registry-neural-search"
    }
}
```

### AWS Credentials
Valid AWS credentials must be available to AWS CLI and SAM CLI. The easiest way to do this is running `aws configure`, or by adding them to `~/.aws/credentials` and exporting the `AWS_PROFILE` variable to the environment.

For more information visit the documentation page:
[Configuration and credential file settings](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-files.html)

### Jupyter Notebook Setup
To use the virtual environment inside Jupyter Notebook, first activate the virtual environment, then create a kernel for it.
```bash
# Install ipykernal and dot-env
pip install ipykernel python-dotenv

# Add the kernel
python3 -m ipykernel install --user --name=<environment name>

# Delete the kernel
jupyter kernelspec uninstall <environment name>
```

### Python Development
Create a virtual environment for Python development.
```bash
# Create a virtual environment
python3.10 -m venv .venv

# Activate the virtual environment
source .venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
```

### Weaviate
Run the command to download a Docker Compose file for Weaviate ([source](https://weaviate.io/developers/weaviate/installation/docker-compose)).
```bash
curl -o docker-compose.yaml "https://configuration.weaviate.io/v2/docker-compose/docker-compose.yml?generative_cohere=false&generative_openai=false&generative_palm=false&gpu_support=false&media_type=text&modules=modules&ner_module=false&qna_module=false&ref2vec_centroid=false&runtime=docker-compose&spellcheck_module=false&sum_module=false&text_module=text2vec-transformers&transformers_model=sentence-transformers-multi-qa-MiniLM-L6-cos-v1&weaviate_version=v1.19.8"
```

Next, run the command to configure Weaviate to persist data and automatically restart on reboot.
```bash
awk '
  /^  weaviate:$/ {
    print
    print "    restart: always"
    print "    volumes:"
    print "      - /data/weaviate:/var/lib/weaviate"
    while(getline && $0 !~ /^  /);
    if ($0 ~ /^  /) {
      print
    }
    next
  }
  /^  t2v-transformers:$/ {
    print
    print "    restart: always"
    while(getline && $0 !~ /^  /);
    if ($0 ~ /^  /) {
      print
    }
    next
  }
  /CLUSTER_HOSTNAME: '\''node1'\''/ {
    print
    print "      AUTOSCHEMA_ENABLED: '\''false'\''"
    next
  }
  /restart: on-failure:0/ {
    next
  }
  1' docker-compose.yaml > docker-compose-temp.yaml && mv docker-compose-temp.yaml docker-compose.yaml
```

Finally, run the command to start Weaviate.
```bash
docker-compose up -d
```

## Usage

### Makefile Usage
```bash
# Deploy the application
make deploy

# Destroy the application
make destroy

# Run the Batch job to load the database, make sure to copy the job ID value
make job.run

# Check the job status with the job ID
make job.status job_id=<job_id>
```

### Docker
Build the application.
```bash
cd tasks/load_odr
docker build -t load_odr:latest .
```
Run the application.
```bash
docker run -d --env-file ../.env load_odr:latest
```

### AWS Deployment
Once an AWS profile is configured and environment variables are available, the application can be deployed using `make`.
```bash
make deploy
```

### CDK Commands

* `npm run build`   compile typescript to js
* `npm run watch`   watch for changes and compile
* `npm run test`    perform the jest unit tests
* `cdk deploy`      deploy this stack to your default AWS account/region
* `cdk diff`        compare deployed stack with current state
* `cdk synth`       emits the synthesized CloudFormation template

## Troubleshooting
* Check your AWS credentials in `~/.aws/credentials`
* Check that the environment variables are available to the services that need them
* Check that the correct environment or interpreter is being used for Python

## References & Links
- [AWS Open Data Registry](https://registry.opendata.aws/)
- [Weaviate Docuentation](https://www.semi.technology/developers/weaviate/current/index.html)
- [Weaviate GraphQL API](https://weaviate.io/developers/weaviate/current/graphql-references/index.html)
- [Weaviate Docker Compose](https://weaviate.io/developers/weaviate/installation/docker-compose)

## Authors
**Primary Contact:** Gregory Lindsey ([@abk7777](https://github.com/abk7777))
