import logging
from typing import Any, Dict, List, Optional, Union

from jsonpath_ng import parse
from cachetools import cached, LRUCache

from stackstate_etl.model.stackstate import (Component, Event,
                                             HealthCheckState, Metric,
                                             Relation)


class TopologyFactory:
    def __init__(self):
        self.components: Dict[str, Component] = {}
        self.relations: Dict[str, Relation] = {}
        self.health: Dict[str, HealthCheckState] = {}
        self.events: List[Event] = []
        self.metrics: List[Metric] = []
        self.lookups: Dict[str, Any] = {}
        self.log = logging.getLogger()

    def jpath(self, path: str, target: Any, default: Any = None) -> Union[Optional[Any], List[Any]]:
        jsonpath_expr = self._get_jsonpath_expr(path)
        matches = jsonpath_expr.find(target)
        if not matches:
            return default
        if len(matches) == 1:
            return matches[0].value
        return [m.value for m in matches]

    @cached(cache=LRUCache(maxsize=100))
    def _get_jsonpath_expr(self, path: str):
        return parse(path)

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
                raise Exception(f"Component '{component.uid}' already exists. No merge flags indicated.")

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
                raise Exception(f"Component ({component_type}, {name}) not found.")
            return None
        else:
            raise Exception(f"More than 1 result found for Component ({component_type}, {name}) search.")

    def get_component_by_name(self, name: str, raise_not_found: bool = True) -> Optional[Component]:
        result = [c for c in self.components.values() if c.get_name() == name]
        if len(result) == 1:
            return result[0]
        elif len(result) == 0:
            if raise_not_found:
                raise Exception(f"Component ({name}) not found.")
            return None
        else:
            raise Exception(f"More than 1 result found for Component ({name}) search.")

    def get_component_by_name_postfix(self, postfix: str) -> Optional[Component]:
        result = [c for c in self.components.values() if c.get_name().endswith(postfix)]
        if len(result) == 1:
            return result[0]
        elif len(result) == 0:
            return None
        else:
            raise Exception(f"More than 1 result found for Component postfix ({postfix}) search.")

    def component_exists(self, uid: str) -> bool:
        return uid in self.components

    def relation_exists(self, source_id: str, target_id: str) -> bool:
        rel_id = f"{source_id} --> {target_id}"
        return rel_id in self.relations

    def add_relation(self, source_id: str, target_id: str, rel_type: str = "uses") -> Relation:
        rel_id = f"{source_id} --> {target_id}"
        if rel_id in self.relations:
            raise Exception(f"Relation '{rel_id}' already exists.")
        relation = Relation({"source_id": source_id, "target_id": target_id, "external_id": rel_id})
        relation.set_type(rel_type)
        self.relations[rel_id] = relation
        return relation

    def add_health(self, health: HealthCheckState):
        if health.check_id in self.health:
            raise Exception(f"Health event '{health.check_id}' already exists.")
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
                if self.component_exists(relation.target_id):
                    self.add_relation(relation.source_id, relation.target_id, relation.get_type())
                else:
                    target_component = self.get_component_by_name(relation.target_id, raise_not_found=False)
                    if target_component:
                        self.add_relation(relation.source_id, target_component.uid, relation.get_type())
                    else:
                        msg = (
                            f"Failed to find related component '{relation.target_id}'. "
                            f"Reference from component {source.uid}."
                        )
                        self.log.error(msg)
                        self.log.error("Current components known in factory:")
                        for uid in self.components.keys():
                            self.log.info(uid)
                        raise Exception(msg)
            source.relations = []

    @staticmethod
    def get_uid(integration: str, uid_type: str, urn_post_fix: str) -> str:
        sanitize_str = TopologyFactory.sanitize(urn_post_fix)
        return f"urn:{integration}:{uid_type}:/{sanitize_str}"

    @staticmethod
    def sanitize(value: str) -> str:
        return value.replace(" ", "_").lower()
