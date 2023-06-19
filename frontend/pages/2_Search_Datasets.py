import streamlit as st
from src.utils import (
    run_semantic_search_query,
    render_results
)

st.markdown("# Search Datasets")

concepts = st.text_input("Search by similarity:")
distance = st.slider("Distance", min_value=0.0, max_value=2.0, value=1.0, step=0.1)
limit = st.number_input(label="Limit", min_value=0, step=1, value=25)
limit = limit if limit > 0 else 500

if concepts:
    datasets = run_semantic_search_query(concepts, limit=limit, distance=distance)
    render_results(datasets, limit=limit, sort_by_distance=True)