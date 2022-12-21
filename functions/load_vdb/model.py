from dataclasses import dataclass
import json
import jmespath
from uuid import uuid4


@dataclass
class UnmarshalledJson:

    __slots__ = "__dict__"

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __str__(self) -> str:
        return json.dumps(self.__dict__)

    def __repr__(self) -> str:
        pass


# Automatically assembles models from json mappings but needs to use jmespath
class JsonToWeaviate:
    def __init__(self, data: dict, mappings: dict, references: dict) -> None:
        self._input = UnmarshalledJson(**data)
        self._mappings = mappings
        self._references = references
        self._build()

    def _build(self):
        self.objects = UnmarshalledJson()
        self._build_objects()
        # set id or ids

        # self.references = UnmarshalledJson()
        # self._build_references()

    def _build_objects(self):
        for map in self._mappings:
            setattr(self.objects, map["class"], UnmarshalledJson())
            if not map["path"]:
                expr = f"[{{{', '.join([f'{k}: {v}' for k, v in map['substitutions'].items()])}}}]"
            else:
                expr = f"map(&{{{', '.join([f'{k}: {v}' for k, v in map['substitutions'].items()])}}}, {map['path']})"
            setattr(
                getattr(self.objects, map["class"]),
                "data",
                self.build_weaviate_object(map["class"], expr, self.input)
            )
            ids = [item["id"] for item in getattr(self.objects, map["class"]).data]
            if len(ids) == 1:
                setattr(getattr(self.objects, map["class"]), "id", ids[0])
            else:
                setattr(getattr(self.objects, map["class"]), "ids", ids)

    def _build_references(self):
        for ref in self._references:
            # # shape reference
            # client.data_object.reference.add(
            #     from_uuid='e067f671-1202-42c6-848b-ff4d1eb804ab',
            #     from_property_name='wroteBooks',
            #     to_uuid='a9c1b714-4f8a-4b01-a930-38b046d69d2d',
            #     from_class_name='Author', # ONLY with Weaviate >= 1.14.0
            #     to_class_name='Book', # ONLY with Weaviate >= 1.14.0
            # )

            pass
        

    @staticmethod
    def build_weaviate_object(class_name, expr, data):
        return [
            {"id": str(uuid4()), "class": class_name, "data": item}
            for item in jmespath.search(expr, data)
        ]

    @property
    def input(self):
        return self._input.__dict__


if __name__ == "__main__":
    from pathlib import Path

    # path = Path(__file__).parent.parent.parent / "___schema.json"
    # with open(path) as file:
    #     schema = json.load(file)

    # open a json file
    path = Path(__file__).parent / "event.json"
    with open(path) as file:
        event = json.load(file)

    data = json.loads(event["Records"][0]["body"])["data"]

    # expr_map = {
    #     "Dataset": "[{name: Name, desc: Description, documentaion: Documentation, updateFrequency: UpdateFrequency, license: License}]",
    #     "list_of_values": "map(&{name: @}, Tags)",
    #     "list_of_objects": "map(&{arn: @.ARN, region: @.region, }, Resources)",
    # }

    mappings = [
        {
            "class": "Dataset",
            "path": None,
            "substitutions": {
                "name": "Name",
                "description": "Description",
                "documentation": "Documentation",
                "updateFrequency": "UpdateFrequency",
                "license": "License",
            },
        },
        {
            "class": "Publisher",
            "path": None,
            "substitutions": {"name": "ManagedBy", "contact": "Contact"},
        },
        {
            "class": "Tag",
            "path": "Tags",
            "substitutions": {
                "name": "@",
            },
        },
        {
            "class": "Resource",
            "path": "Resources",
            "substitutions": {
                "arn": "@.ARN",
                "region": "@.Region",
                "description": "@.Description",
                "type": "@.Type",
            },
        },
    ]

    references = [
        {
            "fromClass": "Dataset",
            "toClass": "Publisher",
            "property": "managedBy",
        },
        {
            "fromClass": "Dataset",
            "toClass": "Tag",
            "property": "hasTag",
        },
        {
            "fromClass": "Dataset",
            "toClass": "Resource",
            "property": "hasResource",
        },
    ]

    req = JsonToWeaviate(data, mappings, references)

    print("")
