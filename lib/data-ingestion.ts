import * as path from 'path';
import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as codepipeline from 'aws-cdk-lib/aws-codepipeline';
import { GitHubSourceAction, GitHubTrigger, S3DeployAction } from 'aws-cdk-lib/aws-codepipeline-actions';
import * as sns from 'aws-cdk-lib/aws-sns';
import { SnsDestination } from 'aws-cdk-lib/aws-s3-notifications';
import { SqsSubscription } from 'aws-cdk-lib/aws-sns-subscriptions';
import * as sqs from 'aws-cdk-lib/aws-sqs';
import { Runtime } from 'aws-cdk-lib/aws-lambda';
import * as python from '@aws-cdk/aws-lambda-python-alpha';
import { SqsEventSource } from 'aws-cdk-lib/aws-lambda-event-sources';


export interface DataIngestionProps {
    repoOwner: string;
    repoName: string;
    dataDirectory?: string;
}

export class DataIngestion extends Construct {
    constructor(scope: Construct, id: string, props: DataIngestionProps) {
        super(scope, id);

        const dataBucket = new s3.Bucket(this, 'DataBucket', {
            removalPolicy: cdk.RemovalPolicy.DESTROY,
            autoDeleteObjects: true,
        });

        const pipeline = new codepipeline.Pipeline(this, 'CodePipeline', {
            artifactBucket: dataBucket,
        });

        const sourceOutput = new codepipeline.Artifact();

        const sourceAction = new GitHubSourceAction({
            actionName: 'GitHub_Source',
            owner: props.repoOwner,
            repo: props.repoName,
            output: sourceOutput,
            branch: 'main',
            oauthToken: cdk.SecretValue.secretsManager('aws-open-data-registry-neural-search-github-token', { jsonField: 'token' }),
            trigger: GitHubTrigger.NONE
        });

        pipeline.addStage({
            stageName: 'Source',
            actions: [sourceAction]
        });

        const deployAction = new S3DeployAction({
            actionName: 'S3DeployAction',
            bucket: dataBucket,
            input: sourceOutput,
            extract: true,
            objectKey: `data/${props.repoOwner}/${props.repoName}`
        });

        pipeline.addStage({
            stageName: 'Deploy',
            actions: [deployAction]
        });

        const dataIngestionTopic = new sns.Topic(this, 'DataIngestionTopic');

        dataBucket.addEventNotification(
            s3.EventType.OBJECT_CREATED,
            new SnsDestination(dataIngestionTopic), {
                prefix: `data/${props.repoOwner}/${props.repoName}/${props.dataDirectory}`, 
                suffix: '.yaml' 
            });

        // create an sqs queue to receive the notifications
        const LoadVdbDLQueue = new sqs.Queue(this, 'LoadVdbDLQueue')
        const loadVdbQueue = new sqs.Queue(this, 'LoadVdbQueue', {
            visibilityTimeout: cdk.Duration.seconds(60),
            deadLetterQueue: {
                queue: LoadVdbDLQueue,
                maxReceiveCount: 3
            }
        });

        // subscribe the queue to the topic
        const loadVdbQueueSub = new SqsSubscription(loadVdbQueue, {
            rawMessageDelivery: true
        });

        dataIngestionTopic.addSubscription(loadVdbQueueSub);

        const loadVdbFunction = new python.PythonFunction(this, 'LoadVdbFunction', {
            description: 'Load Open Data Registry records into Weaviate',
            entry: path.join(__dirname, '../functions/load_vdb'),
            index: 'app.py',
            handler: 'lambda_handler',
            runtime: Runtime.PYTHON_3_9,
        });

        loadVdbFunction.addEventSource(new SqsEventSource(loadVdbQueue));
    }
}
