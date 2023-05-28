search_datasets_query = \
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
                    requesterPays
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

browse_datasets_query = \
"""
{{
    Get {{
        Dataset (
            limit: 1000
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
                    requesterPays
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
        }}
    }}
}}
"""