---
layout: default
title: Component Template
grand_parent: Concepts
parent: Template
nav_order: 5
---

# Component Template

The foundational elements in the StackState [4T Model](https://docs.stackstate.com/use/concepts/4t_data_model) are
[Components](https://docs.stackstate.com/use/concepts/components) and [Relations](https://docs.stackstate.com/use/concepts/relations)

The component template offered by the framework allows for the definition of a componenent to be specified as a spec or
as a code snippet.

| Name        | Type    | Description                                                                                                                                  | 
|-------------|---------|----------------------------------------------------------------------------------------------------------------------------------------------|
| uid         | string  | Required.                                                                                                                                    |
| name        | string  | Required.                                                                                                                                    |
| type        | string  | Required. Except when `mergeable` property set.                                                                                              |
| layer       | string  | Optional. Defaults to global settings.                                                                                                       |
| domain      | string  | Optional. Defaults to global settings.                                                                                                       |
| environment | string  | Optional. Defaults to global settings.                                                                                                       |
| labels      | list    | Optional. Can also be a string expression that resolves to a list.                                                                           |
| identifiers | list    | Optional. Can also be a string expression that resolves to a list. `uid` is automatically added.                                             |
| relations   | list    | Optional. `id` or `name` reference to related component. Use pipe symbol to define relation type. Use '<' to reverse relation.               |
| processor   | code    | Optional. Process `component` object using code to set other properties.                                                                     |
| mergeable   | boolean | Optional. Allows component to be merged into an existing component. Or act as a placeholder until another template provides final component. |

## Component Template Spec

```yaml
etl:
  template:
    components:
      - name: nutanix_disk_template
        spec:
          name: "$.disk_hardware_config.serial_number"
          type: "nutanix-disk"
          uid: "|uid('nutanix', 'disk',item['diskid'])"
          layer: "Nutanix Disks"
          domain: "Nutanix"
          # Note the < symbol to indicated relation reversal
          relations: ["|'<urn:nutanix:host:/%s' % item['node_uuid']"]
          labels:
            - "|'prism:%s' % [jpath('$.cluster_name')]"
          identifiers:
            - "|'urn:nutanix:disk:/%s' % [jpath('$.disk_name')]"
          custom_properties:
            disk_size: "$.disk_size"
            online: "$.online"
```

## Component Template Code

Below is the `code` snippet version of the `spec` in the previous section.
```yaml
etl:
  template:
    components:
      - name: nutanix_disk_template
        code: |
          component.name = jpath("$.disk_hardware_config.serial_number")
          component.set_type("nutanix-disk")
          component.uid =  uid('nutanix', 'disk', item['diskid'])
          component.properties.layer = "Nutanix Disks"
          component.properties.domain = "Nutanix"
          # Note the < symbol to indicated relation reversal
          factory.add_component_relations(component, ['<urn:nutanix:host:/%s' % item['node_uuid']]
          component.properties.add_label_kv("prism", item['cluster_name'])
          component.properties.add_identifier('urn:nutanix:disk:/%s' % jpath('$.disk_name'))
          component.properties.add_property("disk_size", item["disk_size"])
          component.properties.add_property("online", jpath("$.online"))
```

## Mergeable property

It may occur that component information can be derived from serveral queries. The framework allows a component 
to be created only once in the `factory`. This is to prevent common configuration errors. Instead the framework
allows contributors to a component.  These components are marked with the `mergeable` property set to true.

When the ETL processing comes to a final stage, the framework will check that there are not dangling components and
throw an error if found.

```yaml

etl:
  queries:
    - name: snow_ci_relations
      query: "snow_client.get('CI_Relationships')"
      template_refs:
        - snow_farm_to_host_template
  template:
    components:
      - name: snow_farm_to_host_template
        selector: "|item['class'] == 'Farm'"
        spec:
          mergeable: true
          name: "$.parent"
          uid: "|uid('nutanix', 'cluster', item['parent'])"
          relations:
            - "|'%s|based_on' % uid('nutanix', 'host', item['child'])"

```

