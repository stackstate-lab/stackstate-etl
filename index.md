# StackState ETL

## Overview

StackState ETL is framework that enables the extraction and transformation of raw data from a target system
to the StackState 4T model using declarative low-code yaml templates.

The framework offers the capability to load the transformed data to the StackState server with an out-of-the-box
[commandline utility](#commandline-utility) or by using the framework from a 
[StackState Agent Check]([https://docs.stackstate.com/develop/developer-guides/agent_check/agent_checks).
See [StackState ETL Agent Check](https://github.com/stackstate-lab/stackstate-etl-agent-check) for such an
implementation.

## TL;DR

If you learn faster by looking at examples, refer to 
[StackState Nutanxi Agent Check](https://github.com/stackstate-lab/sts-nutanix-agent-checks#template-mappings) for a 
real world example of using StackState ETL.

## Introduction

The framework uses a mix of yaml structures that can have dynamic expressions to derive the final values. The
[Concepts](#concepts) section will elaborate further on the structures and their purpose. First we need to be 
introduced to expressions and the context they are interpreted within.

### Expressions

Expressions take on the form of [Json Path](https://goessner.net/articles/JsonPath/index.html#e2) expressions or
Python Code expressions.

| Type     | Denotation | Comments                                             |
|----------|------------|------------------------------------------------------|
| JsonPath | '$.'       | Any yaml string value starting with                  |
| Python   | '&#124;'   | Any yaml string value starting with a pipe character |


Python expressions are evaluated using a minimal [Python AST Evaluator](https://newville.github.io/asteval/index.html),
while Json Path is evaluated using [jsonpath-ng](https://github.com/h2non/jsonpath-ng#jsonpath-syntax).

### Evaluation Context

Python expressions or code snippets always have access to the following objects in the context,

| Name              | Type                                                               | Description                                                       | 
|-------------------|--------------------------------------------------------------------|-------------------------------------------------------------------|
| factory           | [TopologyFactory](./docs/static/stackstate_etl/model/factory.html) | Registry for 4T elements                                          |
| jpath             | function                                                           | Accepts a json path expression to evaluate against current `item` |
| session           | dict                                                               | Dictionary that exists on within the current ETL definition       |
| global_session    | dict                                                               | Dictionary that exists across all ETL definitions                 |
| uid               | function                                                           | Used to create ids. See TopologyFactory.get_uid(...)              |
| datetime          | [datetime](https://docs.python.org/3/library/datetime.html)        | Module supplies classes for manipulating dates and times.         |
| pytz              | [pytz](https://pythonhosted.org/pytz/)                             | Library allows accurate and cross platform timezone calculations  |
| requests          | [requests](https://requests.readthedocs.io/en/latest/)             | Simple HTTP library                                               |
| pandas            | [pandas](https://pandas.pydata.org/)                               | Data analysis and manipulation tool                               |
| pendulum          | [pendulum](https://pendulum.eustace.io/)                           | Drop-in replacement for the standard datetime class               |
| log               | [Logger](https://docs.python.org/3/library/logging.html)           | Logging                                                           |
| `datasource name` | Any                                                                | Datasource instance as defined in ETL yaml                        |


Including the [builtins](https://newville.github.io/asteval/basics.html#built-in-functions) provided by asteval itself.

As the framework processes rows of data, temporary objects become available depending on current template being evaluated.


| Name              | Type                                                                                                          | Description                           | 
|-------------------|---------------------------------------------------------------------------------------------------------------|---------------------------------------|
| item              | dict                                                                                                          | Dict. Current row from extracted data |
| component         | [Compoment](./docs/static/stackstate_etl/model/stackstate.html#stackstate_etl.model.stackstate.Component)     | Optional                              |
| metric            | [Metric](./docs/static/stackstate_etl/model/stackstate.html#stackstate_etl.model.stackstate.Metric)           | Optional                              |
| event             | [Event](./docs/static/stackstate_etl/model/stackstate.html#stackstate_etl.model.stackstate.Event)             | Optional                              |
| health            | [Health](./docs/static/stackstate_etl/model/stackstate.html#stackstate_etl.model.stackstate.HealthCheckState) | Optional                              |

## Concepts

### Datasource

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
property to be code.  The last line of an expression is the value that is returned.  
Note the `my_static_client` example returns the function as the value.


### Query

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

#### Derived data sets using a processor

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




### Refs

```yaml
etl:
  refs:
    - "module_dir://sts_nutanix_impl.templates"
  ...
```

`refs` is a list of paths referencing other ETL models. The paths have the format of `<prefix>://<dir or file>`

| Prefix      | Description                                     |
|-------------|-------------------------------------------------|
| module_dir  | reads all yaml files from a python module       |
| module_file | reads yaml file from a python module            |
| file        | reads yaml file(s) from location on file system |

### Pre- and Post- Processors

```yaml
etl:
  ...
  pre_processors:
    - name: convert_bytes_function
      code: |
        def bytesto(bytes, to, bsize=1024):
            a = {'k' : 1, 'm': 2, 'g' : 3, 't' : 4, 'p' : 5, 'e' : 6 }
            r = float(bytes)
            for i in range(a[to]):
                r = r / bsize
            return(r)
        global_session["bytesto"] = bytesto
```




### Templates
#### Components
#### Metrics
#### Health
#### Events




## ETL Model Old
The datasources are used by query definitions to fetch rows of data.  For each row of data, several templates can be
defined to transform the row into a 4T model element.  Supported elements are Component, Event, Metric, Health.

The property on definitions can have an expression to derive its final value.  

Processors (code snippets) can be defined at various levels to help with the extraction and transformation of data.

Refs are used to refer to other ETL models for modularity.
 

### Sample ETL Yaml Definition

```yaml
etl:
  refs:
    - "module_dir://sts_nutanix_impl.templates"
  pre_processors:
    - name: convert_bytes_function
      code: |
        def bytesto(bytes, to, bsize=1024):
            a = {'k' : 1, 'm': 2, 'g' : 3, 't' : 4, 'p' : 5, 'e' : 6 }
            r = float(bytes)
            for i in range(a[to]):
                r = r / bsize
            return(r)
        global_session["bytesto"] = bytesto
  datasources:
    - name: nutanix_client
      module: sts_nutanix_impl.client.nutanix_client
      cls: NutanixClient
      init: "NutanixClient(conf.nutanix, log)"
  queries:
    - name: nutanix_disks
      query: "nutanix_client.get(nutanix_client.V2, 'disks')['entities']"
      template_refs:
        - nutanix_disk_template
        - nutanix_disk_online_template
        - nutanix_disk_metric_spec_template
        - nutanix_disk_metric_code_template
  template:
    components:
      - name: nutanix_disk_template
        spec:
          name: "$.disk_hardware_config.serial_number"
          type: "nutanix-disk"
          uid: "|uid('nutanix', 'disk', item['disk_uuid'])"
          layer: "Nutanix Disks"
          labels:
            - "|'prism_cluster:%s' % global_session['cluster_lookup'][jpath('$.cluster_uuid')]"
          custom_properties:
            model: "$.disk_hardware_config.model"
            current_firmware_version: "$.disk_hardware_config.current_firmware_version"
          relations: ["|'<urn:nutanix:host:/%s' % item['node_uuid']"]
    health:
      - name: nutanix_disk_online_template
        spec:
          check_id: "|'%s_online' % item['disk_uuid']"
          check_name: "DiskOnline"
          topo_identifier: "|uid('nutanix', 'disk', item['disk_uuid'])"
          health: "|'CLEAR' if item['online'] else 'WARNING'"
          message: "|'Disk Status is %s' % item['disk_status']"
    metrics:
      - name: nutanix_disk_metric_spec_template
        spec:
          name: "storage.logical_usage_gb"
          metric_type: "gauge"
          value: "|global_session['bytesto'](item['usage_stats']['storage.logical_usage_bytes'], 'g')"
          target_uid: "|uid('nutanix', 'disk', item['disk_uuid'])"
      - name: nutanix_disk_metric_code_template
        code: |
          component_uid = uid('nutanix','disk', item['disk_uuid'])
          bytesto = global_session['bytesto']
          usage_stats = item["usage_stats"]
          factory.add_metric_value("storage.capacity_gb", 
                                    bytesto(usage_stats["storage.capacity_bytes"], 'g'),
                                    target_uid=component_uid)

```

### ETL Execution Logic

![Sequence Diagram](docs/img/sequence_diagram.svg)



## Commandline Utility
## Installation on Python 2.7

StackState Agent 2 supports python 2.7.  StackState ETL is transpiled to python 2.7 code.

From a shell on the agent machine run,

```bash 
/opt/stackstate-agent/embedded/bin/pip install https://github.com/stackstate-lab/stackstate-etl/releases/download/v0.1.0/stackstate-etl-py27-0.1.0.tar.gz
```


### Reference Documentation

See [reference](./docs/static/stackstate_etl/index.html)