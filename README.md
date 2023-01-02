# aws-open-data-registry-neural-search

Semantic search of AWS Open Data Registry datasets using Weaviate.

*Please Note: This project is in development but you can deploy the Weaviate instance from the main branch following the Quickstart.*

## Table of Contents

## Description
Deploy and load a Weaviate instance with [AWS Open Data Registry](https://registry.opendata.aws/) datasets. Find datasets, tutorials, publications and tools & applications using semantic search and natural language processing queries.

## Quickstart
1. Configure your AWS credentials.
2. Add environment variables to `.env`.
3. Run `npm install` to install TypeScript dependencies.
4. Run `cdk deploy` to deploy the cluster.

## Installation
Follow the steps to configure the deployment environment.

### Prerequisites
* Nodejs >= 18.0.0
* TypeScript >= 4.4.3
* AWS CDK >= 2.53.0
* Poetry
* Python 3.9
* AWSCLI
* jq

### Environment Variables

Sensitive environment variables containing secrets like passwords and API keys must be exported to the environment first.

Create a `.env` file in the project root.
```bash
REPO_URL=https://github.com/awslabs/open-data-registry
```

***Important:*** *Always use a `.env` file or AWS SSM Parameter Store or Secrets Manager for sensitive variables like credentials and API keys. Never hard-code them, including when developing. AWS will quarantine an account if any credentials get accidentally exposed and this will cause problems.*

***Make sure that `.env` is listed in `.gitignore`***

#### GitHub Personal Access token
To allow the application to access the AWS Open Data Registry GitHub repository, a personal access token must be created and added to the `.env` file. The token must have permissions for the `repo` scope.

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
The Python development environment is managed by Poetry. To install Poetry, follow the instructions on the [Poetry website](https://python-poetry.org/docs/#installation).

Run the command to install dependencies using Poetry.
```bash
poetry install
```

To activate the virtual environment, run the command.
```bash
poetry shell
```

## Usage

### Docker
Build the application.
```bash
cd tasks/load-odr
docker build -t load-odr:latest .
```
Run the application.
```bash
docker run -d --env-file ../.env load-odr:latest
```

<!-- ### Network Configuration
The only required variable for network configuration is the SUBNET_ID variable which must be present in `.env`. -->

### AWS Deployment
Once an AWS profile is configured and environment variables are available, the application can be deployed using `make`.
```bash
cdk deploy
```

## CDK Commands

* `npm run build`   compile typescript to js
* `npm run watch`   watch for changes and compile
* `npm run test`    perform the jest unit tests
* `cdk deploy`      deploy this stack to your default AWS account/region
* `cdk diff`        compare deployed stack with current state
* `cdk synth`       emits the synthesized CloudFormation template

<!-- ### Makefile Usage
```bash
# Deploy all layers
make deploy

# Delete all layers
make delete
``` -->

## Troubleshooting
* Check your AWS credentials in `~/.aws/credentials`
* Check that the environment variables are available to the services that need them
* Check that the correct environment or interpreter is being used for Python

## References & Links
- [AWS Open Data Registry](https://registry.opendata.aws/)
- [Weaviate Docuentation](https://www.semi.technology/developers/weaviate/current/index.html)
- [Weaviate GraphQL API](https://weaviate.io/developers/weaviate/current/graphql-references/index.html)

## Authors
**Primary Contact:** Gregory Lindsey ([@abk7777](https://github.com/abk7777))
