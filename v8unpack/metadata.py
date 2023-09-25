from enum import Enum
from dataclasses import dataclass


@dataclass
class MetadataType:
    name: str
    uid: str


class MetadataTypes(Enum):
    external_data_processor = MetadataType(
        name='ExternalDataProcessor',
        uid='c3831ec8-d8d5-4f93-8a22-f9bfae07327f')
    external_report = MetadataType(
        name='ExternalReport',
        uid='e41aff26-25cf-4bb6-b6c1-3f478a75f374')
    configuration = MetadataType(
        name='Configuration',
        uid='9cd510cd-abfc-11d4-9434-004095e12fc7')


class MetadataFields(Enum):
    attributes = 1
    tables = 2
    forms = 3
    templates = 4


METADATA = {
    MetadataTypes.external_data_processor: {
        MetadataFields.attributes:
            'ec6bb5e5-b7a8-4d75-bec9-658107a699cf',
        MetadataFields.tables:
            '2bcef0d1-0981-11d6-b9b8-0050bae0a95d',
        MetadataFields.forms:
            'd5b0e5ed-256d-401c-9c36-f630cafd8a62',
        MetadataFields.templates:
            '3daea016-69b7-4ed4-9453-127911372fe6'
    },
    MetadataTypes.external_report: {
        MetadataFields.attributes:
            '7e7123e0-29e2-11d6-a3c7-0050bae0a776',
        MetadataFields.tables:
            'b077d780-29e2-11d6-a3c7-0050bae0a776',
        MetadataFields.forms:
            'a3b368c0-29e2-11d6-a3c7-0050bae0a776',
        MetadataFields.templates:
            '3daea016-69b7-4ed4-9453-127911372fe6'
    },
    MetadataTypes.configuration: {},
}


class MetadataObject:
    # @classmethod
    # def from_container(container: Container):
    #     metadata_object = MetadataObject()
    #     # metadata_object.name = MetadataObject.
    #     return metadata_object

    @staticmethod
    def _read_name(container):
        pass

    def __init__(self) -> None:
        self.name: str
        self.module: str
        self.forms: list[Form]


class Form:
    def __init__(self) -> None:
        self.name: str
        self.module: str


if __name__ == '__main__':
    pass
