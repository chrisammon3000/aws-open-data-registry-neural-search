import { Construct } from 'constructs';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import * as batch from '@aws-cdk/aws-batch-alpha';
import * as ecs from 'aws-cdk-lib/aws-ecs';
import * as iam from 'aws-cdk-lib/aws-iam';


export interface DataIngestionProps {
    repoUrl: string;
    targetDataDirectory: string;
    vpc: ec2.IVpc;
    endpointSsmParamName: string;
}

export class DataIngestion extends Construct {
    constructor(scope: Construct, id: string, props: DataIngestionProps) {
        super(scope, id);

        // create a service role for the Batch compute environment
        const serviceRole = new iam.Role(this, 'OdrDataIngestionServiceRole', {
            assumedBy: new iam.ServicePrincipal('batch.amazonaws.com'),
            managedPolicies: [
                iam.ManagedPolicy.fromAwsManagedPolicyName('service-role/AWSBatchServiceRole')
            ]
        });

        // Create the same compute environment using cfnBatch, assign the workerInstanceRole
        const computeEnvironment = new batch.ComputeEnvironment(this, 'OdrDataComputeEnv', {
            serviceRole,
            computeResources: {
                type: batch.ComputeResourceType.FARGATE_SPOT,
                vpc: props.vpc,
                vpcSubnets: {subnetType: ec2.SubnetType.PUBLIC},
            },
        });

        // Create a Fargate task execution role that aattaches AmazonSSMFullAccess policy
        const executionRole = new iam.Role(this, 'OdrDataIngestionTaskExecutionRole', {
            assumedBy: new iam.ServicePrincipal('ecs-tasks.amazonaws.com'),
            managedPolicies: [
                iam.ManagedPolicy.fromAwsManagedPolicyName('service-role/AmazonECSTaskExecutionRolePolicy')
            ]
        });

        const jobRole = new iam.Role(this, 'OdrDataIngestionJobRole', {
            assumedBy: new iam.ServicePrincipal('ecs-tasks.amazonaws.com'),
            managedPolicies: [
                iam.ManagedPolicy.fromAwsManagedPolicyName('AmazonSSMFullAccess')
            ]
        });

        // create a Batch job definition
        new batch.JobDefinition(this, 'OdrDataIngestionJobDef', {
            jobDefinitionName: 'OdrDataIngestionJobDef',
            platformCapabilities: [batch.PlatformCapabilities.FARGATE],
            container: {
                executionRole: executionRole,
                jobRole: jobRole,
                image: ecs.ContainerImage.fromAsset('./tasks/load-odr'),
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

        // create a Batch job queue
        new batch.JobQueue(this, 'OdrDataIngestionJobQueue', {
            jobQueueName: 'OdrDataIngestionJobQueue',
            computeEnvironments: [
                {
                    computeEnvironment,
                    order: 1
                }
            ]
        });
    }
}
