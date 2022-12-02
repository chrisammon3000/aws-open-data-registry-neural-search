import * as cdk from 'aws-cdk-lib';import * as lambda from 'aws-cdk-lib/aws-lambda';
import { DataIngestion } from './data-ingestion';
import { VectorDatabase } from './vector-database';

const repoOwner: string = 'awslabs';
const repoName: string = 'open-data-registry';
const dataDirectory: string = 'datasets';

export class AwsOpenDataRegistryNeuralSearchStack extends cdk.Stack {
  constructor(scope: cdk.App, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const vectorDatabase = new VectorDatabase(this, 'VectorDatabase');

    const dataIngestion = new DataIngestion(this, 'DataIngestion', {
        repoOwner,
        repoName,
        dataDirectory
    });
    dataIngestion.node.addDependency(vectorDatabase);

  }
}
