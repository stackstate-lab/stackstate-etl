from datetime import datetime
from typing import Any, Dict, List

from schematics import Model
from schematics.transforms import blacklist, wholelist
from schematics.types import (BooleanType, DictType, IntType, ListType,
                              ModelType, StringType)

from stackstate_etl.model.stackstate import (AnyType, Component, Event,
                                             HealthCheckState, Relation,
                                             TimestampType)


class Instance(Model):
    instance_type: str = StringType(required=True, serialized_name="type")
    url: str = StringType(required=True)

    class Options:
        roles = {"public": wholelist()}


class TopologySync(Model):
    start_snapshot: bool = BooleanType(default=True)
    stop_snapshot: bool = BooleanType(default=True)
    instance: Instance = ModelType(Instance, required=True)
    delete_ids: List[str] = ListType(StringType(), default=[])
    components: List[Component] = ListType(ModelType(Component), default=[])
    relations: List[Relation] = ListType(ModelType(Relation), default=[])

    class Options:
        roles = {"public": wholelist()}


class HealthSyncStartSnapshot(Model):
    expiry_interval_s: int = IntType()
    repeat_interval_s: int = IntType(required=True, default=1800)  # 30 Minutes

    class Options:
        roles = {"public": blacklist("expiry_interval_s")}


class HealthStream(Model):
    urn: str = StringType(required=True)
    sub_stream_id: str = StringType()

    class Options:
        roles = {"public": blacklist("sub_stream_id")}


class HealthSync(Model):
    start_snapshot: HealthSyncStartSnapshot = ModelType(HealthSyncStartSnapshot, required=True)
    stop_snapshot: Dict[str, Any] = DictType(AnyType, required=True, default={})
    stream: HealthStream = ModelType(HealthStream, required=True)
    check_states: List[HealthCheckState] = ListType(ModelType(HealthCheckState), default=[])

    class Options:
        roles = {"public": wholelist()}


class ReceiverApi(Model):
    apiKey: str = StringType(required=True)
    collection_timestamp: datetime = TimestampType(required=True)
    internal_hostname: str = StringType(required=True, serialized_name="internalHostname")
    events: Dict[str, List[Event]] = DictType(ListType(ModelType(Event), default=[]), default={})
    metrics: List[Any] = ListType(AnyType(), default=[])
    service_checks: List[Any] = ListType(AnyType(), default=[])
    health: List[HealthSync] = ListType(ModelType(HealthSync), default=[])
    topologies: List[TopologySync] = ListType(ModelType(TopologySync), default=[])

    class Options:
        roles = {"public": wholelist()}


class SyncStats(Model):
    components: int = IntType()
    relations: int = IntType()
    checks: int = IntType()
    events: int = IntType()
    metrics: int = IntType()
    payloads: List[str] = ListType(StringType, default=[])
