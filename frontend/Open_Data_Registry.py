from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv());
import streamlit as st


st.set_page_config(
    page_title="AWS Open Data Registry",
    page_icon="🪐",
)

st.write("# Registry of Open Data on AWS")
st.markdown(
    """https://registry.opendata.aws/ 

A repository of publicly available datasets that are available for access from AWS resources. Note that datasets in this registry are available via AWS resources, but they are not provided by AWS; these datasets are owned and maintained by a variety of government organizations, researchers, businesses, and individuals.

## Search Datasets
Run semantic search queries on the datasets in the registry using the Weaviate knowledge graph.

## Browse Datasets
Browse all available datasets alphabetically.

## GraphQL
Send GraphQL queries with Q&A syntax according to the [Weaviate docs](https://weaviate.io/developers/weaviate/current/graphql-references/index.html).

"""
)