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

```json
{
  "ConnectionArn": "arn:aws:codestar-connections:us-east-1:810526023897:connection/762bde48-8939-41bc-bab4-3bb9d48beac2"
}
```