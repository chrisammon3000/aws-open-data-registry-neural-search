import * as config from '../config.json';
import * as cdk from 'aws-cdk-lib';
import { DataIngestionProps, DataIngestion } from './data-ingestion';
import { VectorDatabase } from './vector-database';

export class AmzOpenDataRegistryNeuralSearchStack extends cdk.Stack {
  constructor(scope: cdk.App, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const vectorDatabase = new VectorDatabase(this, 'VectorDatabase');

    const dataIngestionParams: DataIngestionProps = {
        repoUrl: config.layers.data_ingestion.env.repo_url,
        targetDataDirectory: config.layers.data_ingestion.env.target_data_dir,
        vpc: vectorDatabase.vpc,
        endpointSsmParamName: vectorDatabase.endpointSsmParamName
    };

    const dataIngestion = new DataIngestion(this, 'DataIngestion', dataIngestionParams);
    dataIngestion.node.addDependency(vectorDatabase);

  }
}
