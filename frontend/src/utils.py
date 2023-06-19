import os
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv());
import json
import streamlit as st
import weaviate
from src.queries import search_datasets_query, browse_datasets_query


@st.cache(allow_output_mutation=True)
def get_client():
    return weaviate.Client(os.environ["WEAVIATE_ENDPOINT"])

client = get_client()

def execute_query(query):
    result = client.query.raw(query)
    result = json.dumps(result) \
        .replace('<br>', '') \
        .replace('<br/>', '') \
        .replace(' <br />', '')
    return json.loads(result)

@st.cache(allow_output_mutation=True)
def run_semantic_search_query(concepts, limit=1000, distance=0.8, search_datasets_query=search_datasets_query):

    search_datasets_query = search_datasets_query.format(
        concepts=json.dumps(concepts.split(",")), 
        limit=str(limit),
        distance=str(distance)
        )

    return client.query.raw(search_datasets_query)['data']['Get']['Dataset']

@st.cache(allow_output_mutation=True)
def run_browse_datasets_query():
    return client.query.raw(browse_datasets_query.format())['data']['Get']['Dataset']


def render_results(datasets, limit=None, sort_by_distance=False):
    st.text(f"{len(datasets)} results")
    # if len(datasets) > 0:
    #     with st.expander("Raw JSON"):
    #         st.json(datasets[0], expanded=True)
    if sort_by_distance:
        datasets = sorted(datasets, key=lambda k: k['_additional']['distance'], reverse=True)
    for idx, dataset in enumerate(datasets):
        st.markdown("------------")
        st.markdown(f"### ({idx+1}) {dataset['name']}")
        if '_additional' in dataset:
            st.text(f"Distance: {round(dataset['_additional']['distance'], 2)}")
        st.markdown(
            f"{dataset['description'].replace('<br>', '').replace('<br/>', '')}"
            )
        st.markdown(f"**Managed by:**")
        st.markdown('- '.join([ item['name']+'\n' for item in dataset['managedBy'] ]))
        st.markdown(f"**Tags:**")
        tags = ", ".join([tag for tag in dataset['tags'].split(',') if tag != 'aws-pds'])
        st.markdown(f"{tags}")
        with st.expander("**Documentation**"):
            st.markdown(f"{dataset['documentation']}")
        with st.expander("**Publications**"):
            if dataset['hasPublication'] is not None:
                for publication in dataset['hasPublication']:
                    st.markdown(f"**{publication['title']}**")
                    st.markdown(f"{publication['url']}")
                    st.markdown(f"{publication['authorName']}")
        with st.expander("**Resources**"):
            if dataset['hasResource'] is not None:
                for resource in dataset['hasResource']:
                    st.markdown(f"**{resource['type']}**")
                    st.markdown(f"{resource['description']}")
                    if resource['requesterPays']:
                        st.markdown("**requester pays**")
                    st.code(resource['arn'], language="bash")
                    st.markdown(f"{resource['region']}")
        with st.expander("**Tutorials**"):
            if dataset['hasTutorial'] is not None:
                for tutorial in dataset['hasTutorial']:
                    st.markdown(f"**{tutorial['title']}**")
                    st.markdown(f"{tutorial['url']}")
                    if tutorial['services'] != "null":
                        st.markdown(f"{tutorial['services']}")
        with st.expander("**Tools and Applications**"):
            if dataset['hasToolOrApplication'] is not None:
                for tool in dataset['hasToolOrApplication']:
                    st.markdown(f"**{tool['title']}** ({tool['authorName']})")
                    st.markdown(f"{tool['url']}")
