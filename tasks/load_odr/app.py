import os
import logging
from pathlib import Path
import subprocess
from multiprocessing import cpu_count
import yaml
import json
from json2weaviate import JsonToWeaviate
import weaviate
import boto3

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

REPO_URL = os.environ["REPO_URL"]
TARGET_DATA_DIR = os.environ["TARGET_DATA_DIR"]
WEAVIATE_ENDPOINT_SSM_PARAM = os.environ["WEAVIATE_ENDPOINT_SSM_PARAM"]

try:
    ssm = boto3.client('ssm')
    WEAVIATE_ENDPOINT = ssm.get_parameter(Name=WEAVIATE_ENDPOINT_SSM_PARAM, WithDecryption=False)['Parameter']['Value']
except:
    WEAVIATE_ENDPOINT = os.environ["WEAVIATE_ENDPOINT"]
    
data_dir = Path(__file__).parent

# fix
logger.info(f"Environment variables:\nREPO_URL: {REPO_URL}\nTARGET_DATA_DIR: {TARGET_DATA_DIR}\nWEAVIATE_ENDPOINT: {WEAVIATE_ENDPOINT}")

# configure the batch settings
num_cpus = cpu_count() - 1
client = weaviate.Client(WEAVIATE_ENDPOINT)
client.batch.configure(
    batch_size=10,
    dynamic=True,
    timeout_retries=3,
    num_workers=num_cpus,
    callback=weaviate.util.check_batch_result,
)

# create schema
with open(data_dir / 'schema.json') as f:
    schema = json.load(f)
try:
    client.schema.create(schema)
except Exception as e:
    client.schema.update(schema)

def parse_repo_url(repo_url: str) -> str:
    """Parse the repo URL and return the owner and repository name."""
    owner, repo = repo_url.split("/")[-2:]
    return owner, repo


def load_target_files(target_data_path: Path) -> list:
    """Yields yaml files from the target data path."""
    for file in target_data_path.iterdir():
        if file.suffix in [".yaml", ".yml"]:
            with open(file, "r") as f:
                yield yaml.safe_load(f)


def load_spec(spec_path: Path) -> dict:
    """Load JSON from the spec path."""
    with open(spec_path, "r") as f:
        return json.load(f)


if __name__ == "__main__":
    # get the owner and repo name
    owner, repo = parse_repo_url(REPO_URL)
    clone_target_path = data_dir / "data" / owner / repo
    target_data_path = data_dir / "data" / owner / repo / TARGET_DATA_DIR

    logger.info(f"Cloning {REPO_URL} to {clone_target_path}...")

    # clone github repo from REPO_URL
    subprocess.run(["git", "clone", REPO_URL, str(clone_target_path)])

    # load yaml files as json from the target data path
    files = load_target_files(target_data_path=target_data_path)

    # create data objects
    mappings_spec_path = Path(__file__).parent / "mappings-spec.json"
    references_spec_path = Path(__file__).parent / "references-spec.json"

    factory = JsonToWeaviate(
        mappings=load_spec(mappings_spec_path),
        references=load_spec(references_spec_path),
    )

    logger.info(f"Loading data objects and cross references...")
    num_errors = 0
    max_errors = 5
    with client.batch as batch:
        for idx, file in enumerate(files):
            try:
                # while client.batch.shape
                mapper = JsonToWeaviate.from_json(factory, file)

                # add data objects
                for data_object in mapper.data_objects:
                    batch.add_data_object(
                        data_object["data"],
                        class_name=data_object["class"],
                        uuid=data_object["id"],
                    )

                # add cross references, may not work with autoschema
                for cross_reference in mapper.cross_references:
                    batch.add_reference(
                        from_object_uuid=cross_reference['from_uuid'],
                        from_object_class_name=cross_reference['from_class_name'],
                        from_property_name=cross_reference['from_property_name'],
                        to_object_uuid=cross_reference['to_uuid'],
                        to_object_class_name=cross_reference['to_class_name'],
                    )

            except Exception as e:
                logger.error(f"Error loading file {file}: {e}")
                num_errors += 1
                if num_errors >= max_errors:
                    logger.error(f"Max errors of {max_errors} reached, aborting...")
                    raise e
                continue

    logger.info(f"Loaded {idx + 1} files into Weaviate.")
    exit(0)