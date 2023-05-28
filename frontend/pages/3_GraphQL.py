import streamlit as st
from streamlit_ace import st_ace
from src.queries import browse_datasets_query
from src.utils import (
    execute_query
)

st.markdown("# GraphQL")
st.write("For information on how to use GraphQL with Weaviate, please refer to the [documentation](https://weaviate.io/developers/weaviate/api/graphql).")
st.write("Enter a GraphQL query below:")

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

with st.expander("Example"):
    st.markdown(f"```\n{browse_datasets_query.format()}\n```")
