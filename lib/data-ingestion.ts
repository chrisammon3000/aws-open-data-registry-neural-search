import * as path from 'path';
import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as codepipeline from 'aws-cdk-lib/aws-codepipeline';
import { GitHubSourceAction, GitHubTrigger, S3DeployAction } from 'aws-cdk-lib/aws-codepipeline-actions';
import * as sns from 'aws-cdk-lib/aws-sns';
import { LambdaDestination } from 'aws-cdk-lib/aws-s3-notifications';
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

        // data bucket
        const dataBucket = new s3.Bucket(this, 'DataBucket', {
            removalPolicy: cdk.RemovalPolicy.DESTROY,
            autoDeleteObjects: true,
        });

        // GitHub data ingestion pipeline
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

        // unzips data and puts it in the data bucket
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

        // SNS topic for data ingestion notifications from S3
        const dataIngestionTopic = new sns.Topic(this, 'DataIngestionTopic');

        // receive S3 notifications and publish them to the SNS topic
        const publishRecordsFunction = new python.PythonFunction(this, 'PublishRecordsFunction', {
            description: 'Publish Open Data Registry records to SNS topic',
            entry: path.join(__dirname, '../functions/publish_records'),
            index: 'app.py',
            handler: 'lambda_handler',
            runtime: Runtime.PYTHON_3_9,
            memorySize: 256,
            environment: {
                DATA_INGEST_TOPIC_ARN: dataIngestionTopic.topicArn
            }
        });
        dataBucket.grantRead(publishRecordsFunction);
        dataIngestionTopic.grantPublish(publishRecordsFunction);
        dataBucket.addEventNotification(s3.EventType.OBJECT_CREATED, new LambdaDestination(publishRecordsFunction), {
            prefix: `data/${props.repoOwner}/${props.repoName}/${props.dataDirectory}`, 
            suffix: '.yaml' 
        });

        // SQS queue for published records to load vector database
        const loadVdbDLQueue = new sqs.Queue(this, 'LoadVdbDLQueue')
        const loadVdbQueue = new sqs.Queue(this, 'LoadVdbQueue', {
            visibilityTimeout: cdk.Duration.seconds(60),
            receiveMessageWaitTime: cdk.Duration.seconds(20),
            deadLetterQueue: {
                queue: loadVdbDLQueue,
                maxReceiveCount: 3
            }
        });

        const loadVdbQueueSubscription = new SqsSubscription(loadVdbQueue, {
            rawMessageDelivery: true
        });
        dataIngestionTopic.addSubscription(loadVdbQueueSubscription);

        // insert records to Weaviate vector database
        const loadVdbFunction = new python.PythonFunction(this, 'LoadVdbFunction', {
            description: 'Load Open Data Registry records into Weaviate',
            entry: path.join(__dirname, '../functions/load_vdb'),
            index: 'app.py',
            handler: 'lambda_handler',
            runtime: Runtime.PYTHON_3_9,
            reservedConcurrentExecutions: 1
        });
        loadVdbFunction.addEventSource(new SqsEventSource(loadVdbQueue, {
            batchSize: 10
        }));
    }
}
