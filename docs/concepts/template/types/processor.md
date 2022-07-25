---
layout: default
title: Processor Template
grand_parent: Concepts
parent: Template
nav_order: 7
---

# Processor Template

A Processor template is used for advanced use cases where more control over the processing of the `item` is required.

```yaml
etl:
  template:
    processors:
      - name: nutanix_label_processor_template
        code: |
          component = factory.get_component(uid('nutanix', 'host', item['metadata']['uuid']))
          component.properties.add_label_kv("processor", "label")
      - name: ucmdb_relation_processor_template
        code: |
          if item['type'] == 'dependency':
            src_id = uid("ucmdb", "id", item['end1Id'])
            target_id = uid("ucmdb", "id", item['end2Id'])
            if factory.component_exists(src_id) and factory.component_exists(target_id):
              if not factory.relation_exists(src_id, target_id):
                relation = factory.add_relation(src_id, target_id)
                relation.properties["labels"].append(item['label'])
```
