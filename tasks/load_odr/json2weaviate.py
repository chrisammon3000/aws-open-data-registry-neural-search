import json
import logging
from dataclasses import dataclass
from functools import cached_property
from itertools import chain
from uuid import uuid4
import jmespath

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class JsonModel:
    __slots__ = "__dict__"

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __str__(self) -> str:
        return json.dumps(self.__dict__)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.__dict__})"


# Automatically assembles models from json mappings but needs to use jmespath
class JsonToWeaviate:
    def __init__(self, mappings: dict, references: dict = None, data: dict = None) -> None:
        self._input = JsonModel(**data) if data else None
        self._class_mappings = mappings
        self._ref_mappings = references

        if self._input is not None:
            self.build()

    @classmethod
    def from_json(cls, obj, data: str, mappings: str = None, references: str = None):
        return cls(
            mappings=mappings or obj._class_mappings,
            references=references or obj._ref_mappings,
            data=data,
        )

    def build(self):
        self.classes = JsonModel()
        self._build_objects()

        if self._ref_mappings is not None:
            self._build_references()

    def _build_objects(self):
        for map in self._class_mappings:
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
            setattr(self.classes, map["class"], JsonModel())
            getattr(self.classes, map["class"]).name = map["class"]
            getattr(self.classes, map["class"]).references = None

            # build data objects
            data_objects = self.build_weaviate_object(map["class"], expr, self.input)
            getattr(self.classes, map["class"]).data_objects = data_objects

            # set ids
            ids = [item["id"] for item in getattr(self.classes, map["class"]).data_objects]
            getattr(self.classes, map["class"]).ids = ids

            # set parent alignments
            if par_align is not None:
                getattr(self.classes, map["class"])._parent_align = {
                    align_idx: _id for align_idx, _id in zip(par_align, ids)
                }

    def get_parent_alignment(self, path):
        par_path = ".".join(path.split(".")[:-1])
        child_key = path.split(".")[-1].replace("[]", "")
        align_map = [child_key in item for item in jmespath.search(par_path, self.input)]
        return [idx for idx, i in enumerate(align_map) if i]

    @staticmethod
    def build_weaviate_object(class_name, expr, data):
        return [{"id": str(uuid4()), "class": class_name, "data": item} for item in jmespath.search(expr, data)]

    def _build_references(self):
        for ref_spec in self._ref_mappings:
            # Skip if class is not in JSON
            if not hasattr(self.classes, ref_spec["fromClass"]):
                continue
            getattr(self.classes, ref_spec["fromClass"]).references = JsonModel()
        for ref_spec in self._ref_mappings:
            # Skip if class is not in JSON
            if not hasattr(self.classes, ref_spec["toClass"]):
                continue

            from_uuids = getattr(self.classes, ref_spec["fromClass"]).ids
            to_uuids = getattr(self.classes, ref_spec["toClass"]).ids

            # get alignments
            if hasattr(getattr(self.classes, ref_spec["toClass"]), "_parent_align"):
                to_class_align_idx = getattr(self.classes, ref_spec["toClass"])._parent_align
                from_to_align_map = {from_uuids[k]: v for k, v in to_class_align_idx.items()}

                # match from and to uuids based on index position
                ref = [
                    {
                        "from_uuid": from_uuid,
                        "from_property_name": ref_spec["property"],
                        "to_uuid": to_uuid,
                        "from_class_name": ref_spec["fromClass"],
                        "to_class_name": ref_spec["toClass"],
                    }
                    for from_uuid, to_uuid in from_to_align_map.items()
                ]
            else:
                if len(from_uuids) > 1:
                    logger.warning(f"Multiple UUIDs in source class while setting references: {ref_spec['fromClass']}.")
                ref = [
                    {
                        "from_uuid": from_uuid,
                        "from_property_name": ref_spec["property"],
                        "to_uuid": to_uuid,
                        "from_class_name": ref_spec["fromClass"],
                        "to_class_name": ref_spec["toClass"],
                    }
                    for from_uuid in from_uuids
                    for to_uuid in to_uuids
                ]

            setattr(
                getattr(self.classes, ref_spec["fromClass"]).references,
                ref_spec["property"],
                ref,
            )

    @property
    def input(self):
        return self._input.__dict__

    @cached_property
    def data(self):
        return [*self.data_objects, *self.cross_references]

    @cached_property
    def data_objects(self):
        return list(chain.from_iterable([item.data_objects for item in self.classes.__dict__.values()]))

    @cached_property
    def cross_references(self):
        return list(
            chain.from_iterable(
                [
                    data
                    for item in self.classes.__dict__.values()
                    if item.references is not None
                    for data in item.references.__dict__.values()
                ]
            )
        )

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"
