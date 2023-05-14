import os
from dotenv import load_dotenv, find_dotenv
import json
import streamlit as st
import weaviate
import pandas as pd
from queries import explore_datasets_query

# configure dotenv
load_dotenv(find_dotenv())

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

question_query_template = """
{{
    Get {{
        Dataset(
            ask: {{
                question: "{question}",
                properties: [
                    "description",
                    "tags"
                ]
            }}
        ) {{
            name
            description
            tags
        }}
    }}
}}
"""

def execute_question_query(question):
    return client.query.raw(question_query_template.format(question=question.strip()))

def format_query_result(result):
    df = pd.DataFrame.from_dict(result['data']['Get']['Dataset'])
    df.rename(lambda col: col.capitalize(), axis=1, inplace=True)
    return df


def run_semantic_search(concepts, limit=1000, distance=0.8, explore_datasets_query=explore_datasets_query):

    explore_datasets_query = explore_datasets_query.format(
        concepts=json.dumps(concepts.split(",")), 
        limit=str(limit),
        distance=str(distance)
        )

    return client.query.raw(explore_datasets_query)['data']['Get']['Dataset']