import * as path from 'path';
import cdk = require('aws-cdk-lib');
import { Construct } from 'constructs';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import * as iam from 'aws-cdk-lib/aws-iam';
import { Asset } from 'aws-cdk-lib/aws-s3-assets';
import * as ssm from 'aws-cdk-lib/aws-ssm';

export class VectorDatabase extends Construct {
    public readonly vpc: ec2.IVpc;
    public readonly endpointSsmParamName: string;
    constructor(scope: Construct, id: string) {
        super(scope, id);

        // can move networking resources to a separate construct later; allow DNS resolution
        const vpc = new ec2.Vpc(this, 'VPC', {
            natGateways: 0,
            subnetConfiguration: [{
                name: 'Vpc',
                subnetType: ec2.SubnetType.PUBLIC,
                cidrMask: 24
            }],
            enableDnsHostnames: true,
            enableDnsSupport: true
        });

        // Fargate load task security group
        const loadOdrTaskSecurityGroup = new ec2.SecurityGroup(this, 'LoadOdrTaskSecurityGroup', {
            vpc,
            allowAllOutbound: true,
            description: 'Allow SSH (TCP port 22) in',
        });

        // Weaviate instance security group
        const securityGroup = new ec2.SecurityGroup(this, 'VectorDatabaseSecurityGroup', {
            vpc,
            allowAllOutbound: true,
            description: 'Allow SSH (TCP port 22) in',
        });
        
        // add the load task security group to the weaviate security group
        securityGroup.addIngressRule(
            loadOdrTaskSecurityGroup,
            ec2.Port.tcp(8080),
            'Allow Weaviate access');

        securityGroup.addIngressRule(
            ec2.Peer.ipv4('209.65.62.26/32'), 
            ec2.Port.tcp(22),
            'Allow SSH (TCP port 22) in');

        securityGroup.addIngressRule(
            ec2.Peer.ipv4('209.65.62.26/32'), 
            ec2.Port.tcp(8080),
            'Allow Weaviate access');

        securityGroup.addIngressRule(
            ec2.Peer.ipv4('108.210.70.169/32'), 
            ec2.Port.tcp(22),
            'Allow SSH (TCP port 22) in');

        securityGroup.addIngressRule(
            ec2.Peer.ipv4('108.210.70.169/32'), 
            ec2.Port.tcp(8080),
            'Allow Weaviate access');

        const role = new iam.Role(this, 'Role', {
            assumedBy: new iam.ServicePrincipal('ec2.amazonaws.com'),
            managedPolicies: [
                iam.ManagedPolicy.fromAwsManagedPolicyName('AmazonSSMManagedInstanceCore'),
            ]
        });

        const ami = new ec2.AmazonLinuxImage({
            generation: ec2.AmazonLinuxGeneration.AMAZON_LINUX_2,
            cpuType: ec2.AmazonLinuxCpuType.X86_64
        });

        // TODO add an ebs volume to the instance
        const instance = new ec2.Instance(this, 'VectorDatabase', {
            vpc,
            instanceType: ec2.InstanceType.of(ec2.InstanceClass.M5, ec2.InstanceSize.LARGE),
            machineImage: ami,
            securityGroup,
            keyName: 'aws-open-data-registry-neural-search-key-pair',
            role,
            instanceName: 'aws-odr-vector-database',
            blockDevices: [{
                deviceName: '/dev/xvda',
                volume: ec2.BlockDeviceVolume.ebs(50)
            }]
        });

        const userData = new Asset(this, 'UserData', {
            path: path.join(__dirname, '../src/config.sh')
        });

        const localPath = instance.userData.addS3DownloadCommand({
            bucket: userData.bucket,
            bucketKey: userData.s3ObjectKey
        });

        instance.userData.addExecuteFileCommand({
            filePath: localPath,
            arguments: '--verbose -y'
        });
        userData.grantRead(instance.role);

        // create an elastic IP and associate it with the instance
        const eip = new ec2.CfnEIP(this, 'EIP', {
            domain: 'vpc'
        });

        new ec2.CfnEIPAssociation(this, 'EIPAssociation', {
            allocationId: eip.attrAllocationId,
            instanceId: instance.instanceId
        });

        // Create an SSM paramter with the path `/OdrNeuralSearch/${AWS_REGION}/WeaviateEndpoint
        const endpointValue = `http://${eip.attrPublicIp}:8080`
        const endpointSsmParam = new ssm.StringParameter(this, 'WeaviateEndpoint', {
            parameterName: `/OdrNeuralSearch/${cdk.Aws.REGION}/Endpoint`,
            simpleName: false,
            stringValue: endpointValue
        });
        const endpointSsmParamName = endpointSsmParam.parameterName
        new cdk.CfnOutput(this, 'VectorDatabaseEndpoint', { value: endpointValue });   
    }
}