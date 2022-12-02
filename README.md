# aws-open-data-registry-neural-search

Semantic search of AWS Open Data Registry datasets using Weaviate.

### Notebook Setup
To use the virtual environment inside Jupyter Notebook, first activate the virtual environment, then create a kernel for it.
```bash
# Install ipykernal and dot-env
pip install ipykernel python-dotenv

# Add the kernel
python3 -m ipykernel install --user --name=<environment name>

# Delete the kernel
jupyter kernelspec uninstall <environment name>
```

<!-- ## Useful commands

* `npm run build`   compile typescript to js
* `npm run watch`   watch for changes and compile
* `npm run test`    perform the jest unit tests
* `cdk deploy`      deploy this stack to your default AWS account/region
* `cdk diff`        compare deployed stack with current state
* `cdk synth`       emits the synthesized CloudFormation template -->