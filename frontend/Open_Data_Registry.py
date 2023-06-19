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

## Browse Datasets
Browse all available datasets alphabetically.

## Search Datasets
Run semantic search queries against datasets in the registry.

## GraphQL
Send GraphQL queries directly to Weaviate ([docs](https://weaviate.io/developers/weaviate/current/graphql-references/index.html)).

"""
)