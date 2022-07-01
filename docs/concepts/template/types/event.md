---
layout: default
title: Event Template
grand_parent: Concepts
parent: Template
nav_order: 8
---

# Event Template

Events are sent to StackState using the [Agent Check Event Api](https://docs.stackstate.com/develop/developer-guides/agent_check/agent-check-api#events).

The event template offered by the framework allows for the definition of an event to be specified as a spec.

```yaml
etl:
  template:
    events:
      - name: sample_propery_changed_event
        spec:
          category: "Changes"
          event_type: "ElementPropertiesChanged"
          msg_title: "Host Patched"
          msg_text: "|'%s host was patched' % factory.get_component_by_name(item['name']).uid"
          source: "nutanix"
          source_links:
            - title: "see in nutanix"
              url: "|'https://%s/karbon/v1-beta.1/k8s/clusters/%s' % (nutanix_client.url, item['id'])"
          data:
            old:
              patch_version: "v.1.1.0"
            new:
              patch_version: "v.1.1.2"
          tags:
            - "etl:event"
```


## Event Properties

| Name                | Type                    | Description                                                                                                                                  | 
|---------------------|-------------------------|----------------------------------------------------------------------------------------------------------------------------------------------|
| category            | string                  | Required. Valid values are Activities, Alerts, Anomalies, Changes, Others                                                                    |
| event_type          | string                  | Describes the event being sent. This should generally end with the suffix Event, for example ConfigurationChangedEvent, VersionChangedEvent. |
| msg_title           | string                  | Required. The title of the event.                                                                                                            |
| msg_text            | string                  | Required. The text body of the event. Can be markdown.                                                                                       |
| element_identifiers | list                    | These are used to bind the event to a topology element or elements.                                                                          |
| source_links        | list of EventSourceLink | Optional. A list of links related to the event, for example a dashboard or the event in the source system.                                   |
| source              | string                  | The name of the system from which the event originates, for example AWS, Kubernetes or JIRA                                                  |
| data                | dict                    | Optional. Can be string that evaluates to dict. A list of key/value details about the event, for example a configuration version             |
| tags                | list                    | Optional. Can be string that evalulates to list. A list of key/value tags to associate with the event.                                       |

