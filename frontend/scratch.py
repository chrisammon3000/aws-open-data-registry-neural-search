import json
from utils import (
    execute_query,
    execute_question_query
)


if __name__ == "__main__":

    query = \
    """
    {{
        Get {{
            Dataset(
                limit: 10,
                nearText: {{
                    concepts: {concepts}
                }}
            ) {{
                name
                description
                documentation
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
    concepts = "ocean, atmosphere"
    result = execute_query(query.format(concepts=json.dumps(concepts.split(","))))
    # question = "Which datasets are about space?"
    # data = execute_question_query(questio    print("")
    print("")