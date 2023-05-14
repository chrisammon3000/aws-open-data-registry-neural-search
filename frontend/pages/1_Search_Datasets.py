import json
import streamlit as st
from streamlit_ace import st_ace
from utils import (
    execute_query,
    execute_question_query
)
from queries import explore_datasets_query

from render_results import render_results

st.markdown("# Search Datasets")

concepts = st.text_input("Search by similarity:")
distance = st.slider("Distance", min_value=0.0, max_value=1.0, value=0.8, step=0.1)
limit = st.number_input(label="Limit", min_value=0, step=1, value=25)
limit = limit if limit > 0 else 500

if concepts:
    explore_datasets_query = explore_datasets_query.format(
        concepts=json.dumps(concepts.split(",")), 
        limit=str(limit),
        distance=str(distance)
        )
    result = execute_query(explore_datasets_query)
    datasets = result['data']['Get']['Dataset']

    render_results(datasets, limit=limit)