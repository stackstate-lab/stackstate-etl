---
layout: default
title: Health Template
grand_parent: Concepts
parent: Template
nav_order: 7
---

# Health Template

Health is synchronized with StackState using the [Health-Synchronization](https://docs.stackstate.com/configure/health/health-synchronization) mechanism.

The health template offered by the framework allows for the definition of a heath sync state to be specified as a spec.

```yaml
etl:
  queries:
    - name: nutanix_disks
      query: "nutanix_client.get(nutanix_client.V2, 'disks')['entities']"
      template_refs:
        - nutanix_disk_online_template
  template:
    health:
      - name: nutanix_disk_online_template
        spec:
          check_id: "|'%s_online' % item['disk_uuid']"
          check_name: "DiskOnline"
          topo_identifier: "|uid('nutanix', 'disk', item['disk_uuid'])"
          health: "|'CLEAR' if item['online'] else 'WARNING'"
          message: "|'Disk Status is %s' % item['disk_status']"
```


## Health Properties

| Name            | Type                    | Description                                                                                                                      | 
|-----------------|-------------------------|----------------------------------------------------------------------------------------------------------------------------------|
| check_id        | string                  | Required. Identifier for the check state in the external system                                                                  |
| check_name      | string                  | Required. Name of the external check state.                                                                                      |
| topo_identifier | string                  | Required. Used to bind the check state to a StackState topology element.                                                         |
| message         | string                  | Optional. Message to display in StackState UI. Data will be interpreted as markdown                                              |
| health          | string                  | Required. One of the following StackState Health state values: Clear, Deviating, Critical.                                       |

