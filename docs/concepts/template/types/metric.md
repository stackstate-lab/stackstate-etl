---
layout: default
title: Metric Template
grand_parent: Concepts
parent: Template
nav_order: 6
---

# Metric Template

Metrics are sent to StackState using the [Agent Check Metrics Api](https://docs.stackstate.com/develop/developer-guides/agent_check/agent-check-api#metrics).

The metric template offered by the framework allows for the definition of a metric to be specified as a spec or
as a code snippet.

## Metric Types

| Metric Type | Description                                                      | 
|-------------|------------------------------------------------------------------|
| gauge       | Sample a gauge metric                                            |
| count       | Sample a raw count metric                                        |
| rate        | Sample a point, with the rate calculated at the end of the check |
| increment   | Increment a counter metric                                       |
| decrement   | Decrement a counter metric                                       |
| histogram   | Sample a histogram metric                                        |
| historate   | Sample a histogram based on rate metrics                         |

## Metric Properties

| Name        | Type    | Description                                                                                                                                  | 
|-------------|---------|----------------------------------------------------------------------------------------------------------------------------------------------|
| name        | string  | Required.                                                                                                                                    |
| metric_type | string  | Required.                                                                                                                                    |
| value       | string  | Required. Float as string                                                                                                                    |
| target_uid  | string  | Required. The component targeted by this metric                                                                                              |
| tags        | list    | Optional. Can also be a string expression that resolves to a list.                                                                           |

## Metric Template Spec

Defining a single metric using a `spec`

```yaml
etl:
  queries:
    - name: nutanix_disks
      query: "nutanix_client.get(nutanix_client.V2, 'disks')['entities']"
      template_refs:
        - nutanix_disk_metric_spec_template
  template:
    metrics:
      - name: nutanix_disk_metric_spec_template
        spec:
          name: "storage.logical_usage_gb"
          metric_type: "gauge"
          value: "|global_session['bytesto'](item['usage_stats']['storage.logical_usage_bytes'], 'g')"
          target_uid: "|uid('nutanix', 'disk', item['disk_uuid'])"

```

## Metric Template Code

In many cases, you will need to map several metrics from an `item`. The `code` option can be perfectly used for those
cases.

```yaml
etl:
  queries:
    - name: nutanix_disks
      query: "nutanix_client.get(nutanix_client.V2, 'disks')['entities']"
      template_refs:
        - nutanix_disk_metric_code_template
  template:
    metrics:
      - name: nutanix_disk_metric_code_template
        code: |
          component_uid = uid('nutanix','disk', item['disk_uuid'])
          bytesto = global_session['bytesto']
          usage_stats = item["usage_stats"]
          factory.add_metric_value("storage.capacity_gb", 
                                    bytesto(usage_stats["storage.capacity_bytes"], 'g'),
                                    target_uid=component_uid)
          factory.add_metric_value("storage.free_gb",
                                    bytesto(usage_stats["storage.free_bytes"], 'g'),
                                    target_uid=component_uid)
          factory.add_metric_value("storage.usage_gb",
                                    bytesto(usage_stats["storage.usage_bytes"], 'g'),
                                    target_uid=component_uid)
```
