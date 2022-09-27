import logging

from stackstate_etl.etl.etl_driver import ETLDriver
from stackstate_etl.model.factory import TopologyFactory
from stackstate_etl.model.instance import CliConfiguration
from stackstate_etl.model.stackstate_receiver import SyncStats
from stackstate_etl.stackstate.client import StackStateClient


class CliProcessor:
    def __init__(self, config: CliConfiguration):
        self.config = config
        self.stackstate: StackStateClient = StackStateClient(config.stackstate)
        self.factory: TopologyFactory = TopologyFactory()
        self.log = logging.getLogger()

    def run(self, dry_run=False) -> SyncStats:
        processor = ETLDriver(self.config, self.factory, self.log)
        processor.process()
        stats = self.stackstate.publish(
            list(self.factory.components.values()), list(self.factory.relations.values()), dry_run
        )
        self.stackstate.publish_health_checks(list(self.factory.health.values()), dry_run=dry_run, stats=stats)
        self.stackstate.publish_events(self.factory.events, dry_run=dry_run, stats=stats)
        return self.stackstate.publish_metrics(self.factory.metrics, dry_run=dry_run, stats=stats)
