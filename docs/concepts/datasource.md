---
layout: default
title: Datasource
parent: Concepts
nav_order: 2
---
# Datasource

To extract data from a target system, one usually interacts with a target system's API via some sort of client library 
or SDK. Most moderen systems expose a Rest Api or GQL Api that can be interacted with generic libraries like
[requests](https://requests.readthedocs.io/en/latest/) or [gql](https://gql.readthedocs.io/en/latest/modules/client.html).

The framework allows for the declarative definition of a __Datasource__ to capture the above process.

```yaml
etl:
    datasources:
      - name: nutanix_client
        module: sts_nutanix_impl.client.nutanix_client
        cls: NutanixClient
        init: "NutanixClient(conf.nutanix, log)"
        
      - name: my_rest_client
        init: "requests.Session()"
        
      - name: my_static_client
        init: |
          def generate_data():
            return [{"hostA": 1, "calls": "hostB"}, {"hostB": 2}, {"hostC": 3}]
          generate_data
```

A datasource can reference any Python class that will be passed to the `init` code snippet for instantiation and 
configuration. Or the `init` can create the datasource using arbitrary code.

In the `my_rest_client` example, the `init` does not have to be prefixed with `|` as the framework already expects the
property to be code.  The last line of an expression is the value that is returned, note the `my_static_client` example
returns the function as the value.

Once the datasource is intrepreted, the datasource is available in the evalution context under the specified `name` 

