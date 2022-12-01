import * as cdk from 'aws-cdk-lib';import * as lambda from 'aws-cdk-lib/aws-lambda';
import { DataIngestion } from './data-ingestion';
import { VectorDatabase } from './vector-database';

const repoOwner: string = 'awslabs';
const repoName: string = 'open-data-registry';
const dataDirectory: string = 'datasets';

export class AwsOpenDataRegistryNeuralSearchStack extends cdk.Stack {
  constructor(scope: cdk.App, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const dataIngestion = new DataIngestion(this, 'DataIngestion', {
        repoOwner,
        repoName,
        dataDirectory
    });

    const vectorDatabase = new VectorDatabase(this, 'VectorDatabase');
  }
}



// import * as cdk from 'aws-cdk-lib';
// import { Construct } from 'constructs';
// import * as s3 from 'aws-cdk-lib/aws-s3';
// import * as codepipeline from 'aws-cdk-lib/aws-codepipeline';
// import { GitHubSourceAction, GitHubTrigger, S3DeployAction } from 'aws-cdk-lib/aws-codepipeline-actions';

// export class AwsOpenDataRegistryNeuralSearchStack extends cdk.Stack {
//   constructor(scope: Construct, id: string, props?: cdk.StackProps) {
//     super(scope, id, props);

//     const artifactsBucket = new s3.Bucket(this, 'ArtifactsBucket', {
//         removalPolicy: cdk.RemovalPolicy.DESTROY,
//         autoDeleteObjects: true,
//     });

//     const pipeline = new codepipeline.Pipeline(this, 'CodePipeline', {
//         artifactBucket: artifactsBucket,
//     });

//     const sourceOutput = new codepipeline.Artifact();
//     const sourceAction = new GitHubSourceAction({
//         actionName: 'GitHub_Source',
//         owner: repoOwner,
//         repo: repoName,
//         output: sourceOutput,
//         branch: 'main',
//         oauthToken: cdk.SecretValue.secretsManager('aws-open-data-registry-neural-search-github-token', { jsonField: 'token' }),
//         trigger: GitHubTrigger.NONE
//     });

//     pipeline.addStage({
//         stageName: 'Source',
//         actions: [sourceAction]
//     });

//     const deployAction = new S3DeployAction({
//         actionName: 'S3DeployAction',
//         bucket: artifactsBucket,
//         input: sourceOutput,
//         extract: true,
//         objectKey: `data/${repoOwner}/${repoName}`
//     });

//     pipeline.addStage({
//         stageName: 'Deploy',
//         actions: [deployAction]
//     });

//     // TODO S3 notification to SQS



//     // TODO Lambda SQS consumer

//   }
// }
