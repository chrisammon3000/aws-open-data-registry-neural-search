import * as path from 'path';
import * as config from '../config.json';
import cdk = require('aws-cdk-lib');
import { Construct } from 'constructs';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import * as iam from 'aws-cdk-lib/aws-iam';
import { Asset } from 'aws-cdk-lib/aws-s3-assets';
import * as ssm from 'aws-cdk-lib/aws-ssm';

export class VectorDatabase extends Construct {
    public readonly vpc: ec2.IVpc;
    public readonly endpointSsmParamName: string;
    public readonly loadAmzOdrTaskSecurityGroup: ec2.ISecurityGroup;
    constructor(scope: Construct, id: string) {
        super(scope, id);

        // // can move networking resources to a separate construct later; allow DNS resolution
        // this.vpc = new ec2.Vpc(this, 'VPC', {
        //     natGateways: 0,
        //     subnetConfiguration: [{
        //         name: 'Vpc',
        //         subnetType: ec2.SubnetType.PUBLIC,
        //         cidrMask: 24
        //     }],
        //     enableDnsHostnames: true,
        //     enableDnsSupport: true
        // });

        this.vpc = ec2.Vpc.fromLookup(this, 'VPC', {
            isDefault: true,
          });

        // Weaviate instance security group
        const securityGroup = new ec2.SecurityGroup(this, 'VectorDatabaseSecurityGroup', {
            vpc: this.vpc,
            allowAllOutbound: true,
            description: 'Allow SSH (TCP port 22) in',
        });

        // add the load task security group to the weaviate security group
        securityGroup.addIngressRule(
            ec2.Peer.ipv4('0.0.0.0/0'),
            ec2.Port.tcp(8080),
            'Allow Weaviate access');

        securityGroup.addIngressRule(
            ec2.Peer.ipv4(config.layers.vector_database.env.ssh_cidr),
            ec2.Port.tcp(22),
            'Allow SSH');

        const role = new iam.Role(this, 'Role', {
            assumedBy: new iam.ServicePrincipal('ec2.amazonaws.com'),
            managedPolicies: [
                iam.ManagedPolicy.fromAwsManagedPolicyName('AmazonSSMManagedInstanceCore'),
            ]
        });
        
        const ami = ec2.MachineImage.fromSsmParameter('/aws/service/canonical/ubuntu/eks/20.04/1.21/stable/current/amd64/hvm/ebs-gp2/ami-id');
        const instance = new ec2.Instance(this, 'VectorDatabase', {
            vpc: this.vpc,
            instanceType: ec2.InstanceType.of(ec2.InstanceClass.M6I, ec2.InstanceSize.XLARGE),
            machineImage: ami,
            securityGroup,
            keyName: config.layers.vector_database.env.ssh_key_name,
            role,
            instanceName: 'amz-odr-vector-database',
            blockDevices: [{
                deviceName: '/dev/xvda',
                volume: ec2.BlockDeviceVolume.ebs(16)
            }]
        });

        const userData = new Asset(this, 'UserData', {
            path: path.join(__dirname, '../src/config.sh')
        });

        const localPath = instance.userData.addS3DownloadCommand({
            bucket: userData.bucket,
            bucketKey: userData.s3ObjectKey
        });

                // provision Ubuntu 20.04 LTS
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

        // instance ID ssm parameter
        const instanceIdSsmParam = new ssm.StringParameter(this, 'InstanceId', {
            parameterName: `/${config.tags.org}/${config.tags.app}/InstanceId`,
            simpleName: false,
            stringValue: instance.instanceId
        });

        const endpointValue = `http://${eip.attrPublicIp}:8080`
        const endpointSsmParam = new ssm.StringParameter(this, 'WeaviateEndpoint', {
            parameterName: `/${config.tags.org}/${config.tags.app}/WeaviateEndpoint`,
            simpleName: false,
            stringValue: endpointValue
        });
        this.endpointSsmParamName = endpointSsmParam.parameterName
        new cdk.CfnOutput(this, 'VectorDatabaseEndpoint', { value: endpointValue });
    }
}