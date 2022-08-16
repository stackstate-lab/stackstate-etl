from schematics import Model
from schematics.types import IntType, ModelType, StringType, URLType

from stackstate_etl.model.etl import ETL


class HealthSyncSpec(Model):
    source_name: str = StringType(required=True, default="static_health")
    stream_id: str = StringType(required=True)
    expiry_interval_seconds: int = IntType(required=False, default=0)  # Never
    repeat_interval_seconds: int = IntType(required=False, default=1800)  # 30 Minutes


class StackStateSpec(Model):
    receiver_url: str = URLType(required=True)
    api_key: str = StringType(required=True)
    instance_type: str = StringType()
    instance_url: str = StringType()
    health_sync: HealthSyncSpec = ModelType(HealthSyncSpec, required=False, default=None)
    internal_hostname: str = StringType(required=True, default="localhost")


class InstanceInfo(Model):
    domain: str = StringType(default="ETL")
    layer: str = StringType(default="ETL")
    environment: str = StringType(default="production")
    factory_mode: str = StringType(default="Strict", choices=["Strict", "Lenient", "Ignore"])
    etl: ETL = ModelType(ETL, required=True)


class CliConfiguration(InstanceInfo):
    stackstate: StackStateSpec = ModelType(StackStateSpec, required=True)
