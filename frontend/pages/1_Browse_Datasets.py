import streamlit as st
from streamlit_ace import st_ace
from utils import (
    execute_query
)

st.markdown("# Explore Datasets")
# st.sidebar.header("Explore Datasets")

query = st_ace(
    language="python",
    theme="twilight",
    keybinding="vscode",
    tab_size=4
)

if query:
    result = execute_query(query)
    data = result['data']['Get']['Dataset']
    st.json(data)
    # with st.container():
    #     for dataset in data:
    #         st.markdown(f"## {dataset['name']}")
    #         st.markdown(f"{dataset['description']}")

# {
#     Get {
#         Dataset(limit: 3) {
#             name
#             description
#         }
#     }
# }
