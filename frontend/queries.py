explore_datasets_query = \
"""
{{
    Get {{
        Dataset(
            limit: {limit},
            nearText: {{
                concepts: {concepts}
                distance: {distance}
            }}
        ) {{
            name
            description
            documentation
            tags
            managedBy {{
                ... on Publisher {{
                    name
                }}
            }}
            hasResource {{
                ... on Resource {{
                    arn
                    region
                    description
                    type
                }}
            }}
            hasTutorial {{
                ... on Tutorial {{
                    title
                    url
                    services
                }}
            }}
            hasPublication {{
                ... on Publication {{
                    title
                    url
                    authorName
                }}
            }}
            hasToolOrApplication {{
                ... on ToolOrApplication {{
                    title
                    url
                    authorName
                }}   
            }}
            _additional {{
                distance
            }}
        }}
    }}
}}
"""