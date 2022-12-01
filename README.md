# Welcome to your CDK TypeScript project

This is a blank project for CDK development with TypeScript.

The `cdk.json` file tells the CDK Toolkit how to execute your app.

## Useful commands

* `npm run build`   compile typescript to js
* `npm run watch`   watch for changes and compile
* `npm run test`    perform the jest unit tests
* `cdk deploy`      deploy this stack to your default AWS account/region
* `cdk diff`        compare deployed stack with current state
* `cdk synth`       emits the synthesized CloudFormation template

## Create GitHub Connection
```bash
aws codestar-connections create-connection --provider-type GitHub --connection-name aws-open-data-registry-neural-stack
```

## To Do
- [ ] Automate SecretsManager secrets creation for
    - [ ] GitHub PAT
    - [ ] EC2 KeyPair
- [ ] Add SQS subscription to topic, use SQS fo lambda