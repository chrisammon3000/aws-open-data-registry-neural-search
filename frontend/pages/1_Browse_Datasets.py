import streamlit as st
from src.utils import (
    run_browse_datasets_query,
    render_results
)

st.markdown("# Browse Datasets")

datasets = run_browse_datasets_query()
render_results(datasets)