import logging
from typing import Any, Dict, List, Optional, Union

from cachetools import LRUCache, keys
from jsonpath_ng import parse

from stackstate_etl.model.stackstate import (
    Component,
    Event,
    HealthCheckState,
    Metric,
    Relation,
)

STRICT = "Strict"
LENIENT = "Lenient"
IGNORE = "Ignore"


class TopologyFactory:
    def __init__(self, mode=STRICT):
        self.mode = mode
        self.components: Dict[str, Component] = {}
        self.relations: Dict[str, Relation] = {}
        self.health: Dict[str, HealthCheckState] = {}
        self.events: List[Event] = []
        self.metrics: List[Metric] = []
        self.lookups: Dict[str, Any] = {}
        self.log = logging.getLogger()
        self.jpath_cache = LRUCache(maxsize=500)

    def jpath(self, path: str, target: Any, default: Any = None) -> Union[Optional[Any], List[Any]]:
        jsonpath_expr = self._get_jsonpath_expr(path)
        matches = jsonpath_expr.find(target)
        if not matches:
            return default
        if len(matches) == 1:
            return matches[0].value
        return [m.value for m in matches]

    def _get_jsonpath_expr(self, path):
        key = keys.hashkey(path)
        expression = self.jpath_cache.get(key, None)
        if expression is None:
            expression = parse(path)
            self.jpath_cache[key] = expression
        return expression

    def add_event(self, event: Event):
        self.events.append(event)

    def add_metric(self, metric: Metric):
        self.metrics.append(metric)

    def add_metric_value(
        self, name: str, value: float, metric_type: str = "gauge", tags: List[str] = None, target_uid=None
    ):
        metric = Metric()
        metric.name = name
        metric.value = value
        metric.metric_type = metric_type
        metric.target_uid = target_uid
        if tags:
            metric.tags = tags
        self.metrics.append(metric)

    def add_component(self, component: Component):
        if component is None:
            raise Exception("Component cannot be None.")
        existing_component = self.components.get(component.uid, None)
        if existing_component is not None:
            if component.mergeable:
                existing_component.merge(component)
                component = existing_component
            elif existing_component.mergeable:
                component.merge(existing_component)
            else:
                self._handle_error(f"Component '{component.uid}' already exists. No merge flags indicated.")

        component.validate()
        self.components[component.uid] = component

    def get_component(self, uid: str) -> Component:
        return self.components[uid]

    def get_component_by_name_and_type(
        self, component_type: str, name: str, raise_not_found: bool = True
    ) -> Optional[Component]:
        result = [c for c in self.components.values() if c.component_type == component_type and c.get_name() == name]
        if len(result) == 1:
            return result[0]
        elif len(result) == 0:
            if raise_not_found:
                self._handle_error(f"Component ({component_type}, {name}) not found.")
            return None
        else:
            msg = f"More than 1 result found for Component ({component_type}, {name}) search."
            return self._handle_multiple_results_error(msg, result)

    def get_component_by_name(self, name: str, raise_not_found: bool = True) -> Optional[Component]:
        result = [c for c in self.components.values() if c.get_name() == name]
        if len(result) == 1:
            return result[0]
        elif len(result) == 0:
            if raise_not_found:
                self._handle_error(f"Component {name} not found.")
            return None
        else:
            msg = f"More than 1 result found for Component {name} search."
            return self._handle_multiple_results_error(msg, result)

    def get_component_by_name_postfix(self, postfix: str) -> Optional[Component]:
        result = [c for c in self.components.values() if c.get_name().endswith(postfix)]
        if len(result) == 1:
            return result[0]
        elif len(result) == 0:
            return None
        else:
            msg = f"More than 1 result found for Component postfix ({postfix}) search."
            return self._handle_multiple_results_error(msg, result)

    def component_exists(self, uid: str) -> bool:
        return uid in self.components

    @staticmethod
    def new_component() -> Component:
        return Component()

    def get_relation(self, source_id: str, target_id: str) -> Relation:
        rel_id = f"{source_id} --> {target_id}"
        return self.relations[rel_id]

    def relation_exists(self, source_id: str, target_id: str) -> bool:
        rel_id = f"{source_id} --> {target_id}"
        return rel_id in self.relations

    def add_relation(self, source_id: str, target_id: str, rel_type: str = "uses") -> Relation:
        rel_id = f"{source_id} --> {target_id}"
        if rel_id in self.relations:
            self._handle_error(f"Relation '{rel_id}' already exists.")
            return self.relations[rel_id]
        relation = Relation({"source_id": source_id, "target_id": target_id, "external_id": rel_id})
        relation.set_type(rel_type)
        self.relations[rel_id] = relation
        return relation

    def add_health(self, health: HealthCheckState):
        if health.check_id in self.health:
            self._handle_error(f"Health event '{health.check_id}' already exists.")
            return
        self.health[health.check_id] = health

    @staticmethod
    def add_component_relations(component: Component, relations: List[str]):
        for relation in relations:
            rel_parts = relation.split("|")
            rel_type = "uses"
            if len(rel_parts) == 2:
                rel_type = rel_parts[1]
            reverse = False
            if rel_parts[0].startswith("<"):
                reverse = True
                rel_parts[0] = rel_parts[0][1:]

            if reverse:
                rel_id = f"{rel_parts[0]} --> {component.uid}"
                relation = Relation({"source_id": rel_parts[0], "target_id": component.uid, "external_id": rel_id})
            else:
                rel_id = f"{component.uid} --> {rel_parts[0]}"
                relation = Relation({"source_id": component.uid, "target_id": rel_parts[0], "external_id": rel_id})
            relation.set_type(rel_type)
            component.relations.append(relation)

    def resolve_relations(self):
        components: List[Component] = self.components.values()
        for source in components:
            for relation in source.relations:
                resolve_id = relation.target_id
                if source.uid == resolve_id:
                    # There was a reverse relation '<' indicator
                    resolve_id = relation.source_id
                if self.component_exists(resolve_id):
                    self.add_relation(relation.source_id, relation.target_id, relation.get_type())
                else:
                    target_component = self.get_component_by_name(resolve_id, raise_not_found=False)
                    if target_component:
                        self.add_relation(relation.source_id, target_component.uid, relation.get_type())
                    else:
                        msg = (
                            f"Failed to find related component '{resolve_id}'. "
                            f"Reference from component {source.uid}."
                        )
                        if self.mode == STRICT:
                            self.log.error(msg)
                            self.log.error("Current components known in factory:")
                            for uid in self.components.keys():
                                self.log.info(uid)
                        self._handle_error(msg)
            source.relations = []

    def _handle_error(self, msg):
        if self.mode == STRICT:
            raise Exception(msg)
        elif self.mode == LENIENT:
            self.log.warning(f"{msg}. Ignoring...")
        else:
            self.log.debug(f"{msg}. Ignoring...")

    def _handle_multiple_results_error(self, msg, result) -> Any:
        if self.mode == IGNORE:
            self.log.debug(f"{msg}, but returning first in list '{result[0].uid}'.")
            return result[0]
        elif self.mode == LENIENT:
            self.log.warning(f"{msg}, but returning first in list '{result[0].uid}'.")
            return result[0]
        else:
            raise Exception(msg)

    @staticmethod
    def get_uid(integration: str, uid_type: str, urn_post_fix: str) -> str:
        sanitize_str = TopologyFactory.sanitize(urn_post_fix)
        return f"urn:{integration}:{uid_type}:/{sanitize_str}"

    @staticmethod
    def sanitize(value: str) -> str:
        return value.replace(" ", "_").lower()
