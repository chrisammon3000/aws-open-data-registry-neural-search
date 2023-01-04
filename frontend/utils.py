import os
from dotenv import load_dotenv, find_dotenv
import json
import streamlit as st
import weaviate
import pandas as pd

# configure dotenv
load_dotenv(find_dotenv())

@st.cache
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
