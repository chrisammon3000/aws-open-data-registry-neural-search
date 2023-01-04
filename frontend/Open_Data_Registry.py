import os
from dotenv import load_dotenv, find_dotenv
import streamlit as st

# configure dotenv
load_dotenv(find_dotenv())

st.set_page_config(
    page_title="AWS Open Data Registry",
    page_icon="🪐",
)

st.write("# AWS Open Data Registry")
st.markdown(
    """# Registry of Open Data on AWS 

A repository of publicly available datasets that are available for access from AWS resources. Note that datasets in this registry are available via AWS resources, but they are not provided by AWS; these datasets are owned and maintained by a variety of government organizations, researchers, businesses, and individuals.

## Browse Datasets
View specific datasets by selecting a category from the sidebar.

## Explore
Send GraphQL queries with Q&A syntax according to the [Weaviate docs](https://weaviate.io/developers/weaviate/current/graphql-references/index.html).

    """
)


# dataframe = pd.DataFrame(
#     np.random.randn(10, 20),
#     columns=('col %d' % i for i in range(20))
# )
# st.dataframe(dataframe.style.highlight_max(axis=0))
# st.table(dataframe)

# chart_data = pd.DataFrame(
#     np.random.randn(20, 3),
#     columns=['a', 'b', 'c'])

# st.line_chart(chart_data)

# map_data = pd.DataFrame(
#     np.random.randn(100, 2) / [49, 55] + [37.76, -122.4],
#     columns=['lat', 'lon'])

# st.map(map_data)

# x = st.slider('x')  # 👈 this is a widget
# st.write(x, 'squared is', x * x)

# st.text_input("What's your name", key='name')
# type(st.session_state.name)

# if st.checkbox('Show dataframe'):
#     chart_data = pd.DataFrame(
#        np.random.randn(20, 3),
#        columns=['a', 'b', 'c'])

#     chart_data

# df = pd.DataFrame({
#     'first column': [1, 2, 3, 4],
#     'second column': [10, 20, 30, 40]
#     })

# option = st.selectbox(
#     'Which number do you like best?',
#      df['first column'])

# 'You selected: ', option

# add_selectbox = st.sidebar.selectbox(
#     'How would you like to be contacted?',
#     ('Email', 'Home phone', 'Mobile phone')
# )

# add_slider = st.sidebar.slider(
#     'Select a range of values',
#     0.0, 100.0, (25.0, 75.0)
# )

# left_col, right_col = st.columns(2)
# left_col.button('Press me!')

# with right_col:
#     chosen = st.radio(
#         'Sorting hat',
#         ('Gryffindor', 'Hufflepuff', 'Ravenclaw', 'Slytherin'))

# import time

# latest_iteration = st.empty()
# bar = st.progress(0)

# for i in range(100):
#     latest_iteration.text(f'Iteration {i+1}')
#     bar.progress(i+1)
#     time.sleep(0.1)

@st.cache
def my_slow_function():
    time.sleep(5)
    return 42