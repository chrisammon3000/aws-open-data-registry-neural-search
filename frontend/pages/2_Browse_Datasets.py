import streamlit as st
import pandas as pd
import streamlit as st
from streamlit_ace import st_ace
from utils import (
    execute_query,
    run_semantic_search
)


st.markdown("# Browse Datasets")

option = st.selectbox(label='Select one:', options=['Name', 'Topic', 'Publisher']) == 'Name'

if option == "Name":
    st.write('You selected:', option)

if option == "Topic":
    st.write('You selected:', option)

if option == "Publisher":
    st.write('You selected:', option)



# # Example for selecting a category by dropdown
# data = {'Name': ['John', 'Anna', 'Peter', 'Linda'],
#         'Age': [28, 24, 35, 32],
#         'City': ['New York', 'Paris', 'Berlin', 'London']}
# df = pd.DataFrame(data)

# option = st.selectbox(
#     'Browse by name:',
#      df['Name'])
# st.write('You selected:', option)

# option = st.selectbox(
#     'Browse by publisher:',
#      df['Name'])
# st.write('You selected:', option)

# option = st.selectbox(
#     'Browse by ADX category:',
#      df['Name'])
# st.write('You selected:', option)

