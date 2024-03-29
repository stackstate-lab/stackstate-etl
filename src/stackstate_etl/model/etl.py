from typing import Any, Dict, List, Union

from schematics import Model
from schematics.types import (
    BooleanType,
    DictType,
    ListType,
    ModelType,
    StringType,
    UnionType,
)

from stackstate_etl.model.stackstate import EVENT_CATEGORY_CHOICES, AnyType


class DataSource(Model):
    name: str = StringType(required=True)
    module: str = StringType()
    cls: str = StringType()
    init: str = StringType(required=True)


class Query(Model):
    name: str = StringType(required=True)
    query: str = StringType(required=True)
    processor: str = StringType(required=False)
    template_refs: List[str] = ListType(StringType(), required=True, default=[])


class ComponentTemplateSpec(Model):
    name: str = StringType(required=True)
    component_type: str = StringType(required=False, serialized_name="type")
    uid: str = StringType(required=True)
    layer: str = StringType()
    domain: str = StringType()
    environment: str = StringType()
    labels: Union[str, List[str]] = UnionType((StringType, ListType(StringType)), default=[])
    identifiers: Union[str, List[str]] = UnionType((StringType, ListType(StringType)), default=[])
    relations: Union[str, List[str]] = UnionType((StringType, ListType(StringType)), default=[])
    custom_properties: Union[str, Dict[str, Any]] = UnionType((StringType, DictType(AnyType)), default={})
    mergeable: bool = BooleanType(default=False)
    processor: str = StringType()


class ComponentTemplate(Model):
    name: str = StringType(required=True)
    selector: str = StringType(default=None)
    spec = ModelType(ComponentTemplateSpec)
    code = StringType()


class ProcessorTemplate(Model):
    name: str = StringType(required=True)
    selector: str = StringType(default=None)
    code = StringType(required=True)


class EventSourceLink(Model):
    title: str = StringType(required=True)
    url: str = StringType(required=True)


class EventTemplateSpec(Model):
    category: str = StringType(required=True, choices=EVENT_CATEGORY_CHOICES)
    event_type: str = StringType(required=True)
    msg_title: str = StringType(required=True)
    msg_text: str = StringType(required=True)
    element_identifiers: Union[str, List[str]] = UnionType((StringType, ListType(StringType)), default=[])
    source: str = StringType(required=True, default="ETL")
    source_links: List[EventSourceLink] = ListType(ModelType(EventSourceLink, default=[]))
    data: Union[str, Dict[str, Any]] = UnionType((StringType, DictType(AnyType)), default={})
    tags: Union[str, List[str]] = UnionType((StringType, ListType(StringType)), default=[])


class EventTemplate(Model):
    name: str = StringType(required=True)
    selector: str = StringType(default=None)
    spec = ModelType(EventTemplateSpec)


class HealthTemplateSpec(Model):
    check_id: str = StringType(required=True)
    check_name: str = StringType(required=True)
    topo_identifier: str = StringType(required=True)
    message: str = StringType(required=False)
    health: str = StringType(required=True)


class HealthTemplate(Model):
    name: str = StringType(required=True)
    selector: str = StringType(default=None)
    spec = ModelType(HealthTemplateSpec)


class MetricTemplateSpec(Model):
    name: str = StringType(required=True)
    metric_type: str = StringType(required=True)
    value: str = StringType(required=True)
    target_uid: str = StringType(required=True)
    tags: Union[str, List[str]] = UnionType((StringType, ListType(StringType)), default=[])


class MetricTemplate(Model):
    name: str = StringType(required=True)
    selector: str = StringType(default=None)
    spec = ModelType(MetricTemplateSpec)
    code = StringType()


class ProcessorSpec(Model):
    name: str = StringType(required=True)
    code = StringType()


class Template(Model):
    components: List[ComponentTemplate] = ListType(ModelType(ComponentTemplate), default=[])
    processors: List[ProcessorTemplate] = ListType(ModelType(ProcessorTemplate), default=[])
    metrics: List[MetricTemplate] = ListType(ModelType(MetricTemplate), default=[])
    events: List[EventTemplate] = ListType(ModelType(EventTemplate), default=[])
    health: List[HealthTemplate] = ListType(ModelType(HealthTemplate), default=[])


class ETL(Model):
    source: str = StringType(default="Unknown")
    refs: List[str] = ListType(StringType(), default=[])
    pre_processors: List[ProcessorSpec] = ListType(ModelType(ProcessorSpec), default=[])
    post_processors: List[ProcessorSpec] = ListType(ModelType(ProcessorSpec), default=[])
    datasources: List[DataSource] = ListType(ModelType(DataSource), default=[])
    queries: List[Query] = ListType(ModelType(Query), default=[])
    template: Template = ModelType(Template)
