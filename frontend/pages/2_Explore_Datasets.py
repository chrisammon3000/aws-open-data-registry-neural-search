import json
import streamlit as st
from streamlit_ace import st_ace
from utils import (
    execute_query,
    execute_question_query
)

st.markdown("# Explore Datasets")
# st.sidebar.header("Explore Datasets")

query = \
"""
{{
    Get {{
        Dataset(
            limit: {limit},
            nearText: {{
                concepts: {concepts}
                distance: {distance}
            }}
        ) {{
            name
            description
            documentation
            managedBy {{
                ... on Publisher {{
                    name
                }}
            }}
            hasResource {{
                ... on Resource {{
                    arn
                    region
                    description
                    type
                }}
            }}
            hasTutorial {{
                ... on Tutorial {{
                    title
                    url
                }}
            }}
            hasPublication {{
                ... on Publication {{
                    title
                    url
                    authorName
                }}
            }}
            hasToolOrApplication {{
                ... on ToolOrApplication {{
                    title
                    url
                    authorName
                }}   
            }}
            _additional {{
                distance
            }}
        }}
    }}
}}
"""


concepts = st.text_input("Search by similarity:")
distance = st.slider("Distance", min_value=0.0, max_value=1.0, value=0.8, step=0.1)
limit = st.number_input(label="Limit", min_value=0, step=1, value=25)
limit = limit if limit > 0 else 500


if concepts:
    query = query.format(
        concepts=json.dumps(concepts.split(",")), 
        limit=str(limit),
        distance=str(distance)
        )
    result = execute_query(query)
    datasets = result['data']['Get']['Dataset']
    if limit:
        st.text(f"{len(datasets)} results")
    if len(datasets) > 0:
        with st.expander("Raw JSON"):
            st.json(datasets[0], expanded=True)
    for idx, dataset in enumerate(datasets):
        st.markdown("------------")
        st.markdown(f"### ({idx+1}) {dataset['name']}")
        st.text(f"Distance: {round(dataset['_additional']['distance'], 2)}")
        st.markdown(
            f"{dataset['description'].replace('<br>', '').replace('<br/>', '')}"
            )
        st.markdown(f"**Managed by:**")
        st.markdown('- '.join([ item['name']+'\n' for item in dataset['managedBy'] ]))
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
                    st.code(resource['arn'], language="bash")
                    st.markdown(f"{resource['region']}")
        with st.expander("**Tutorials**"):
            if dataset['hasTutorial'] is not None:
                for tutorial in dataset['hasTutorial']:
                    st.markdown(f"**{tutorial['title']}**")
                    st.markdown(f"{tutorial['url']}")
        with st.expander("**Tools and Applications**"):
            if dataset['hasToolOrApplication'] is not None:
                for tool in dataset['hasToolOrApplication']:
                    st.markdown(f"**{tool['title']}** ({tool['authorName']})")
                    st.markdown(f"{tool['url']}")
 