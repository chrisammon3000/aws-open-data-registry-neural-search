import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as codepipeline from 'aws-cdk-lib/aws-codepipeline';
import { GitHubSourceAction, GitHubTrigger, S3DeployAction } from 'aws-cdk-lib/aws-codepipeline-actions';

const repoOwner: string = 'awslabs';
const repoName: string = 'open-data-registry';

export class AwsOpenDataRegistryNeuralSearchStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const artifactsBucket = new s3.Bucket(this, 'ArtifactsBucket', {
        removalPolicy: cdk.RemovalPolicy.DESTROY,
        autoDeleteObjects: true,
    });

    const pipeline = new codepipeline.Pipeline(this, 'CodePipeline', {
        artifactBucket: artifactsBucket,
    });

    const sourceOutput = new codepipeline.Artifact();
    const sourceAction = new GitHubSourceAction({
        actionName: 'GitHub_Source',
        owner: repoOwner,
        repo: repoName,
        output: sourceOutput,
        branch: 'main',
        oauthToken: cdk.SecretValue.secretsManager('aws-open-data-registry-neural-search-github-token', { jsonField: 'token' }),
        trigger: GitHubTrigger.NONE
    });

    pipeline.addStage({
        stageName: 'Source',
        actions: [sourceAction]
    });

    // TODO select S3 prefix
    const deployAction = new S3DeployAction({
        actionName: 'S3DeployAction',
        bucket: artifactsBucket,
        input: sourceOutput,
        extract: true,
        objectKey: `data/${repoOwner}/${repoName}`
    });

    pipeline.addStage({
        stageName: 'Deploy',
        actions: [deployAction]
    });

    // TODO S3 notification for Lambda



    // TODO Lambda function for loading records

    // example resource
    // const queue = new sqs.Queue(this, 'AwsOpenDataRegistryNeuralSearchQueue', {
    //   visibilityTimeout: cdk.Duration.seconds(300)
    // });
  }
}
