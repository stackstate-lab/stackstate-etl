---
layout: default
title: Template
parent: Concepts
nav_order: 4
has_children: true
permalink: /docs/concepts/template
---

# Templates

Transforming data from a target system entails manipulation and mapping of the data to another form.
In StackState ETL the target form is Component, Event, Metric or Health 4T element.

The framework allows for the declarative definition of a __Template__ to capture the above process.

```yaml
etl:
  template:
    components:
      - name: name_of_template
        selector: "|item['class']=='disk'"
      ...
    health:
      ...
    metrics:
      ...
    events:
      ...
```

Every template must have a `name` property.  An optional `selector` expression can be set to indicate whether the 
template should be applied for the current `item` from the query. 

