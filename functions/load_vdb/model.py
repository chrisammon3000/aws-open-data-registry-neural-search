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
    def __init__(self, mappings: dict, references: dict = None, data: dict = None) -> None:
        self._input = UnmarshalledJson(**data) if data else None
        self._mappings = mappings
        self._references = references

        if self._input is not None:
            self._build()

    @classmethod
    def from_json(cls, obj, data: str, mappings: str = None, references: str = None):
        return cls(
            mappings=mappings or obj._mappings,
            references=references or obj._references,
            data=data
        )

    def _build(self):
        self.classes = UnmarshalledJson()
        self._build_objects()

        if self._references is not None:
            self._build_references()

    def _build_objects(self):
        for map in self._mappings:
            setattr(self.classes, map["class"], UnmarshalledJson())
            if not map["path"]:
                expr = f"[{{{', '.join([f'{k}: {v}' for k, v in map['substitutions'].items()])}}}]"
            else:
                expr = f"map(&{{{', '.join([f'{k}: {v}' for k, v in map['substitutions'].items()])}}}, {map['path']})"
            setattr(
                getattr(self.classes, map["class"]),
                "data_objects",
                self.build_weaviate_object(map["class"], expr, self.input)
            )
            ids = [item["id"] for item in getattr(getattr(self.classes, map["class"]), "data_objects")]

            # set ids
            if len(ids) == 1:
                setattr(getattr(self.classes, map["class"]), "id", ids[0])
            else:
                setattr(getattr(self.classes, map["class"]), "ids", ids)

    def _build_references(self):
        for ref_spec in self._references:
            setattr(getattr(self.classes, ref_spec["fromClass"]), "references", UnmarshalledJson())
        for ref_spec in self._references:
            # # request reference
            # client.data_object.reference.add(
            #     from_uuid='e067f671-1202-42c6-848b-ff4d1eb804ab',
            #     from_property_name='wroteBooks',
            #     to_uuid='a9c1b714-4f8a-4b01-a930-38b046d69d2d',
            #     from_class_name='Author', # ONLY with Weaviate >= 1.14.0
            #     to_class_name='Book', # ONLY with Weaviate >= 1.14.0
            # )
            if hasattr(getattr(self.classes, ref_spec["toClass"]), 'id'):
                to_uuids = [getattr(getattr(self.classes, ref_spec["toClass"]), 'id')]
            elif hasattr(getattr(self.classes, ref_spec["toClass"]), 'ids'):
                to_uuids = getattr(getattr(self.classes, ref_spec["toClass"]), 'ids')

            ref = [ {
                "from_uuid": getattr(self.classes, ref_spec["fromClass"]).id,
                "from_property_name": ref_spec["property"],
                "to_uuid": to_uuid,
                "from_class_name": ref_spec["fromClass"],
                "to_class_name": ref_spec["toClass"],
            } for to_uuid in to_uuids ]
            setattr(getattr(getattr(self.classes, ref_spec["fromClass"]), "references"), ref_spec["property"], ref)
        

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

    # open a json file
    path = Path(__file__).parent / "event.json"
    with open(path) as file:
        event = json.load(file)

    data = json.loads(event["Records"][0]["body"])["data"]

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

    factory = JsonToWeaviate(mappings, references)
    builder = JsonToWeaviate.from_json(factory, data)

    print("")
