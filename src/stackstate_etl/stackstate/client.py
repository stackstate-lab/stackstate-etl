import datetime
import json
import logging
import zlib
from hashlib import md5
from typing import Dict, List
from urllib.parse import quote

import requests

from stackstate_etl.model.instance import StackStateSpec
from stackstate_etl.model.stackstate import (
    Component,
    Event,
    HealthCheckState,
    Metric,
    Relation,
)
from stackstate_etl.model.stackstate_receiver import (
    HealthStream,
    HealthSync,
    HealthSyncStartSnapshot,
    Instance,
    ReceiverApi,
    SyncStats,
    TopologySync,
)


class StackStateClient:
    def __init__(self, config: StackStateSpec):
        self.config = config
        self.intake_url = f"{self.config.receiver_url}/stsAgent/intake?api_key={self.config.api_key}"

    def publish_health_checks(
        self, health_checks: List[HealthCheckState], dry_run=False, stats=SyncStats()
    ) -> SyncStats:
        stats.checks = len(health_checks)
        payload = self._prepare_health_sync_payload(health_checks)
        return self._post_data(payload, dry_run, stats)

    def publish_events(self, events: List[Event], dry_run=False, stats=SyncStats()) -> SyncStats:
        stats.events = len(events)
        payload = self._prepare_event_sync_payload(events)
        return self._post_data(payload, dry_run, stats)

    def publish_metrics(self, metrics: List[Metric], dry_run=False, stats=SyncStats()) -> SyncStats:
        stats.metrics = len(metrics)
        payload = self._prepare_metric_sync_payload(metrics)
        return self._post_data(payload, dry_run, stats)

    def publish(
        self, components: List[Component], relations: List[Relation], dry_run=False, stats=SyncStats()
    ) -> SyncStats:
        stats.components = len(components)
        stats.relations = len(relations)
        payload = self._prepare_topo_payload(components, relations)
        return self._post_data(payload, dry_run, stats)

    def _post_data(self, payload: ReceiverApi, dry_run: bool, stats: SyncStats) -> SyncStats:
        if dry_run:
            stats.payloads.append(json.dumps(payload.to_primitive(role="public"), indent=4))
            return stats
        serialized_payload = json.dumps(payload.to_primitive(role="public"))

        zipped = zlib.compress(serialized_payload.encode("utf-8"))
        logging.debug(
            "payload_size=%d, compressed_size=%d, compression_ratio=%.3f"
            % (len(serialized_payload), len(zipped), float(len(serialized_payload)) / float(len(zipped)))
        )
        headers: Dict[str, str] = {
            "Content-Type": "application/json",
            "Content-Encoding": "deflate",
            "Content-MD5": md5(zipped).hexdigest(),
        }
        self._handle_failed_call(requests.post(self.intake_url, data=zipped, headers=headers))
        return stats

    def _prepare_health_sync_payload(self, checks: List[HealthCheckState]) -> ReceiverApi:
        health_stream = HealthStream()
        spec = self.config.health_sync
        encoded_source = quote(spec.source_name, safe="")
        encoded_stream = quote(spec.stream_id, safe="")
        health_stream.urn = f"urn:health:{encoded_source}:{encoded_stream}"

        start_snapshot = HealthSyncStartSnapshot()
        start_snapshot.expiry_interval_s = spec.expiry_interval_seconds
        start_snapshot.repeat_interval_s = spec.repeat_interval_seconds

        sync = HealthSync()
        sync.start_snapshot = start_snapshot
        sync.stream = health_stream
        sync.check_states = checks

        payload = self._prepare_receiver_payload()
        payload.health = [sync]
        return payload

    def _prepare_event_sync_payload(self, events: List[Event]) -> ReceiverApi:
        payload = self._prepare_receiver_payload()
        for event in events:
            event_list = payload.events.setdefault(event.event_type, [])
            event_list.append(event)
        return payload

    def _prepare_metric_sync_payload(self, metrics: List[Metric]) -> ReceiverApi:
        payload = self._prepare_receiver_payload()
        for metric in metrics:
            timestamp_in_secs = int(round(metric.timestamp.timestamp()))
            metric_list = {
                metric.name,
                timestamp_in_secs,
                metric.value,
                {"hostname": metric.target_uid, "tags": metric.tags, "type": metric.metric_type},
            }
            payload.metrics.append(metric_list)
        return payload

    def _prepare_topo_payload(self, components: List[Component], relations: List[Relation]) -> ReceiverApi:
        instance = Instance()
        instance.instance_type = self.config.instance_type
        instance.url = self.config.instance_url

        topology_sync = TopologySync()
        topology_sync.instance = instance
        topology_sync.components = components
        topology_sync.relations = relations

        payload = self._prepare_receiver_payload()
        payload.topologies = [topology_sync]
        return payload

    def _prepare_receiver_payload(self) -> ReceiverApi:
        payload = ReceiverApi()
        payload.apiKey = self.config.api_key
        payload.collection_timestamp = datetime.datetime.now()
        payload.internal_hostname = self.config.internal_hostname
        return payload

    @staticmethod
    def _handle_failed_call(response: requests.Response) -> requests.Response:
        if not response.ok:
            msg = "Failed to call [%s] . Status code %s" % (
                response.url,
                response.status_code,
            )
            logging.error(msg)
            logging.error("Response: %s" % response.text)
            raise Exception(msg)
        return response
