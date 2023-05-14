import streamlit as st

def render_results(datasets, limit):
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
        st.markdown(f"**Tags:**")
        # st.markdown('- '.join([ item['name']+'\n' for item in dataset['hasTag'] ]))
        st.markdown(f"{dataset['tags']}")
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
                    if tutorial['services'] != "null":
                        st.markdown(f"{tutorial['services']}")
        with st.expander("**Tools and Applications**"):
            if dataset['hasToolOrApplication'] is not None:
                for tool in dataset['hasToolOrApplication']:
                    st.markdown(f"**{tool['title']}** ({tool['authorName']})")
                    st.markdown(f"{tool['url']}")
