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
    def __init__(
        self, mappings: dict, references: dict = None, data: dict = None
    ) -> None:
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
            data=data,
        )

    def _build(self):
        self.classes = UnmarshalledJson()
        self._build_objects()

        if self._references is not None:
            self._build_references()

    def _build_objects(self):
        for map in self._mappings:

            # build search expressions
            if not map["path"]:
                expr = f"[{{{', '.join([f'{k}: {v}' for k, v in map['substitutions'].items()])}}}]"
                par_align = None
            elif jmespath.search(map["path"], self.input) is None:
                # Skip if path is not in JSON
                continue
            else:
                expr = f"map(&{{{', '.join([f'{k}: {v}' for k, v in map['substitutions'].items()])}}}, {map['path']})"

                # get parent array alignment for setting correct references
                if "[]." in map["path"]:
                    par_align = self.get_parent_alignment(map["path"])

            # build class
            setattr(self.classes, map["class"], UnmarshalledJson())

            # build data objects
            data_objects = self.build_weaviate_object(map["class"], expr, self.input)
            setattr(getattr(self.classes, map["class"]), "data_objects", data_objects)

            # set ids
            ids = [
                item["id"]
                for item in getattr(getattr(self.classes, map["class"]), "data_objects")
            ]
            setattr(getattr(self.classes, map["class"]), "ids", ids)

            # set parent alignments
            if par_align is not None:
                setattr(getattr(self.classes, map["class"]), "_parent_align", { align_idx: _id for align_idx, _id in zip(par_align, ids) })


    def get_parent_alignment(self, path):
        par_path = ".".join(path.split(".")[:-1])
        child_key = path.split(".")[-1].replace("[]", "")
        align_map = [
            child_key in item.keys() for item in jmespath.search(par_path, self.input)
        ]
        return [idx for idx, i in enumerate(align_map) if i]

    # TODO need a way of handling arrays inside arrays: Services class is an example
    @staticmethod
    def build_weaviate_object(class_name, expr, data):
        return [
            {"id": str(uuid4()), "class": class_name, "data": item}
            for item in jmespath.search(expr, data)
        ]

    def _build_references(self):
        for ref_spec in self._references:
            # Skip if class is not in JSON
            if not hasattr(self.classes, ref_spec["fromClass"]):
                continue
            setattr(
                getattr(self.classes, ref_spec["fromClass"]),
                "references",
                UnmarshalledJson(),
            )
        for ref_spec in self._references:
            # Skip if class is not in JSON
            if not hasattr(self.classes, ref_spec["toClass"]):
                continue

            from_uuids = getattr(getattr(self.classes, ref_spec["fromClass"]), "ids")
            to_uuids = getattr(getattr(self.classes, ref_spec["toClass"]), "ids")

            # get alignments
            if hasattr(getattr(self.classes, ref_spec["toClass"]), "_parent_align"):
                to_class_align_idx = getattr(getattr(self.classes, ref_spec["toClass"]), "_parent_align")
                from_to_align_map = { from_uuids[k]: v for k, v in to_class_align_idx.items() }

                # match from and to uuids based on index position
                ref = [
                    {
                        "from_uuid": from_uuid,
                        "from_property_name": ref_spec["property"],
                        "to_uuid": to_uuid,
                        "from_class_name": ref_spec["fromClass"],
                        "to_class_name": ref_spec["toClass"],
                    } for from_uuid, to_uuid in from_to_align_map.items()
                ]
            else:
                # TODO nested list comprehension results in a cartesion product, but so far it's
                # TODO only been tested with len(from_uuids) == 1. May want to test n:n relationships and possibly optimized this for specific conditions: 1:1, 1:n, n:1, n:n
                ref = [
                    {
                        "from_uuid": from_uuid,
                        "from_property_name": ref_spec["property"],
                        "to_uuid": to_uuid,
                        "from_class_name": ref_spec["fromClass"],
                        "to_class_name": ref_spec["toClass"],
                    } for from_uuid in from_uuids for to_uuid in to_uuids
                ]

            setattr(
                getattr(getattr(self.classes, ref_spec["fromClass"]), "references"),
                ref_spec["property"],
                ref,
            )

    @property
    def input(self):
        return self._input.__dict__

    # TODO polish this
    @property
    def records(self):
        return [item.data_objects for item in self.classes.__dict__.values()]


if __name__ == "__main__":
    from pathlib import Path

    # # open a json file
    # path = Path(__file__).parent / "event.json"
    # with open(path) as file:
    #     event = json.load(file)

    # data = json.loads(event["Records"][0]["body"])["data"]

    with open("___data/output/aws-odr.json") as f:
        data_objs = json.load(f)
    data = data_objs[2]

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
        {
            "class": "Tutorial",
            "path": "DataAtWork.Tutorials",
            "substitutions": {
                "title": "@.Title",
                "url": "@.URL",
                "authorName": "@.AuthorName",
                "authorUrl": "@.AuthorURL",
            },
        },
        {
            "class": "Publication",
            "path": "DataAtWork.Publications",
            "substitutions": {
                "title": "@.Title",
                "url": "@.URL",
                "authorName": "@.AuthorName",
                "authorUrl": "@.AuthorURL",
            },
        },
        {
            "class": "ToolOrApplication",
            "path": 'DataAtWork."Tools & Applications"',
            "substitutions": {
                "title": "@.Title",
                "url": "@.URL",
                "authorName": "@.AuthorName",
                "authorUrl": "@.AuthorURL",
            },
        },
        {
            "class": "Service",
            "path": "DataAtWork.Tutorials[].Services[]",
            "substitutions": {"name": "@"},
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
        {
            "fromClass": "Dataset",
            "toClass": "Tutorial",
            "property": "hasTutorial",
        },
        {
            "fromClass": "Tutorial",
            "toClass": "Service",
            "property": "usesService",
        },
    ]

    builders = []
    for idx, data in enumerate(data_objs):
        factory = JsonToWeaviate(mappings, references)
        builder = JsonToWeaviate.from_json(factory, data)
        builders.append(builder)
        with open(f"___data/output/all_data/all-records-{idx}.json", "w") as f:
            json.dump(builder.records, f, indent=4)

        if idx == 10:
            break

    print("")
