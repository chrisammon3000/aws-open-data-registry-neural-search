import * as dotenv from 'dotenv';
import * as cdk from 'aws-cdk-lib';
import { DataIngestionProps, DataIngestion } from './data-ingestion';
import { VectorDatabase } from './vector-database';

dotenv.config();

export class AwsOpenDataRegistryNeuralSearchStack extends cdk.Stack {
  constructor(scope: cdk.App, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const vectorDatabase = new VectorDatabase(this, 'VectorStorage');

    const dataIngestionParams: DataIngestionProps = {
        repoUrl: process.env.REPO_URL!,
        targetDataDirectory: process.env.TARGET_DATA_DIR!,
        vpc: vectorDatabase.vpc,
        endpointSsmParamName: vectorDatabase.endpointSsmParamName
    };

    const dataIngestion = new DataIngestion(this, 'DataIngestion', dataIngestionParams);
    dataIngestion.node.addDependency(vectorDatabase);

  }
}
