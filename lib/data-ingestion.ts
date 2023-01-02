import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as ecs from 'aws-cdk-lib/aws-ecs';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import * as iam from 'aws-cdk-lib/aws-iam';


export interface DataIngestionProps {
    repoUrl: string;
    targetDataDirectory: string;
    endpointSsmParamName: string;
    vpc: ec2.IVpc;
}

export class DataIngestion extends Construct {
    constructor(scope: Construct, id: string, props: DataIngestionProps) {
        super(scope, id);

        // create a Fargate task definition
        const taskDefinition = new ecs.FargateTaskDefinition(this, 'OdrDataIngestionTaskDef', {
            memoryLimitMiB: 2048,
            cpu: 512
        });

        // add SSM GetParameter permissions to the task role for all resources
        taskDefinition.taskRole.attachInlinePolicy(new iam.Policy(this, 'OdrDataIngestionTaskRolePolicy', {
            statements: [
                new iam.PolicyStatement({
                    actions: ['ssm:GetParameter'],
                    resources: ['*']
                })
            ]
        }));

        // add a container to the task definition from local Dockerfile
        taskDefinition.addContainer('OdrDataIngestionApp', {
            image: ecs.ContainerImage.fromAsset('./tasks/load-odr'),
            environment: {
                REPO_URL: props.repoUrl,
                TARGET_DATA_DIR: props.targetDataDirectory,
                WEAVIATE_ENDPOINT_SSM_PARAM: props.endpointSsmParamName
            },
            logging: new ecs.AwsLogDriver({
                streamPrefix: 'OdrDataIngestionApp'
            })
        });

        // create a network ECS cluster for the fargate task
        const cluster = new ecs.Cluster(this, 'OdrDataIngestionCluster', {
            clusterName: 'OdrDataIngestionCluster',
            vpc: props.vpc,
            containerInsights: true
        });

        // create a CFN output for the custer name
        new cdk.CfnOutput(this, 'OdrDataIngestionClusterName', {
            value: cluster.clusterName
        });
    }
}
