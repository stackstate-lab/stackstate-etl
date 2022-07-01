---
layout: default
title: Query
parent: Concepts
nav_order: 3
---

# Query

Extracting data from a target system entails making requests to the target system for the desired data.

The framework allows for the declarative definition of a __Query__ to capture the above process.  

```yaml 
etl:
  queries:
    - name: nutanix_hosts
      query: "|my_static_client()"
      template_refs:
        - host_template
        - metric_template
```

The `query` can make use of a datasource to make a request. The result must always be a list of dictionary objects.
`template_refs` reference the names of templates that will process each item in the list to create 4T model elements.
Namely component, health, metric, event.  The framework will iterate the list and pass each item to the template via
the execution context under the variable `item`

## Derived data sets using a processor

The list of items received from a datasource can sometimes contain other list that can lead to the creation or 
enhancement of 4T model elements.  In this case, a query can define a `processor`

```yaml
etl:
  queries:
    - name: nutanix_clusters
      query: "nutanix_client.get_clusters()"
      processor: |
        rackable_units = session.setdefault("rackable_units", {})
        rackable_units[item["uuid"]] = item["rackable_units"]
      template_refs:
        - nutanix_cluster_template
    - name: nutanix_rackable_units  
      query: |
        results = []
        for cluster, units in session["rackable_units"].items():
          [py_.set_(n, "cluster_uuid", cluster) for n in units]
          results.extend(units)
        results
      template_refs:
        - nutanix_rackable_unit_template
```

## Processing item without using templates

The `processor` can also be used to process an item from the query directly. Using the `factory` to interact with 4T
elements.

```yaml
etl:
  queries:
    - name: snow_ci_relation_labels
      query: "snow_client.get_labels()"
      processor: |
        ctype, uid_func = session['type_lookup'][item['class']]
        cid = None
        if ctype == 'nutanix-vm' and not item['name'].startswith("NTNX"):
          cid = "urn:host:/%s" % item['name'].lower()
        else:
          cid = uid_func(item['name'])
        if cid is not None and factory.component_exists(cid):
          target_component = factory.get_component(cid)
          target_component.properties.labels.extend(item['labels'])
        else:
          log.error("Failed to lookup type '%s' with name '%s' and component id '%s'" % (ctype, item['name'], cid))
      template_refs: []
```

The above example illustrates using the result of a query to add labels to an existing component in the factory.
