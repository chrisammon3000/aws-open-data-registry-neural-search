import * as config from '../config.json';
import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import * as batch from '@aws-cdk/aws-batch-alpha';
import * as ecs from 'aws-cdk-lib/aws-ecs';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as ssm from 'aws-cdk-lib/aws-ssm';


export interface DataIngestionProps {
    repoUrl: string;
    targetDataDirectory: string;
    vpc: ec2.Vpc;
    endpointSsmParamName: string;
}

export class DataIngestion extends Construct {
    constructor(scope: Construct, id: string, props: DataIngestionProps) {
        super(scope, id);

        const serviceRole = new iam.Role(this, 'AmzOdrDataIngestionServiceRole', {
            assumedBy: new iam.ServicePrincipal('batch.amazonaws.com'),
            managedPolicies: [
                iam.ManagedPolicy.fromAwsManagedPolicyName('service-role/AWSBatchServiceRole')
            ]
        });

        const computeEnvironment = new batch.ComputeEnvironment(this, 'AmzOdrDataComputeEnv', {
            serviceRole,
            computeResources: {
                type: batch.ComputeResourceType.FARGATE_SPOT,
                vpc: props.vpc,
                vpcSubnets: {subnetType: ec2.SubnetType.PUBLIC},
            },
        });

        const executionRole = new iam.Role(this, 'AmzOdrDataIngestionTaskExecutionRole', {
            assumedBy: new iam.ServicePrincipal('ecs-tasks.amazonaws.com'),
            managedPolicies: [
                iam.ManagedPolicy.fromAwsManagedPolicyName('service-role/AmazonECSTaskExecutionRolePolicy')
            ]
        });

        const jobRole = new iam.Role(this, 'AmzOdrDataIngestionJobRole', {
            assumedBy: new iam.ServicePrincipal('ecs-tasks.amazonaws.com'),
            managedPolicies: [
                iam.ManagedPolicy.fromAwsManagedPolicyName('AmazonSSMFullAccess')
            ]
        });

        new batch.JobDefinition(this, 'AmzOdrDataIngestionJobDef', {
            jobDefinitionName: 'AmzOdrDataIngestionJobDef',
            platformCapabilities: [batch.PlatformCapabilities.FARGATE],
            container: {
                executionRole: executionRole,
                jobRole: jobRole,
                image: ecs.ContainerImage.fromAsset('./tasks/load_odr'),
                environment: {
                    REPO_URL: props.repoUrl,
                    TARGET_DATA_DIR: props.targetDataDirectory,
                    WEAVIATE_ENDPOINT_SSM_PARAM: props.endpointSsmParamName
                },
                assignPublicIp: true,
                logConfiguration: {
                    logDriver: batch.LogDriver.AWSLOGS,
                },
            }
        });
        new ssm.StringParameter(this, 'AmzOdrDataIngestionJobDefArnParam', {
            parameterName: `/${config.tags.org}/${config.tags.app}/AmzOdrDataIngestionJobDefArn`,
            stringValue: `arn:aws:batch:${cdk.Aws.REGION}:${cdk.Aws.ACCOUNT_ID}:job-definition/AmzOdrDataIngestionJobDef`,
        });

        new batch.JobQueue(this, 'AmzOdrDataIngestionJobQueue', {
            jobQueueName: 'AmzOdrDataIngestionJobQueue',
            computeEnvironments: [
                {
                    computeEnvironment,
                    order: 1
                }
            ]
        });
        new ssm.StringParameter(this, 'AmzOdrDataIngestionJobQueueArnParam', {
            parameterName: `/${config.tags.org}/${config.tags.app}/AmzOdrDataIngestionJobQueueArn`,
            stringValue: `arn:aws:batch:${cdk.Aws.REGION}:${cdk.Aws.ACCOUNT_ID}:job-queue/AmzOdrDataIngestionJobQueue`,
        });

    }
}
