---
layout: default
title: Expressions
has_children: false
nav_exclude: false
parent: Concepts
nav_order: 1
---

# Expressions

Expressions take on the form of [Json Path](https://goessner.net/articles/JsonPath/index.html#e2) expressions or
Python Code expressions.

| Type     | Denotation | Comments                                             |
|----------|------------|------------------------------------------------------|
| JsonPath | '$.'       | Any yaml string value starting with                  |
| Python   | '&#124;'   | Any yaml string value starting with a pipe character |


Python expressions are evaluated using a minimal [Python AST Evaluator](https://newville.github.io/asteval/index.html),
while Json Path is evaluated using [jsonpath-ng](https://github.com/h2non/jsonpath-ng#jsonpath-syntax).

# Evaluation Context

StackState ETL makes available handy open-source libraies to help you with your transformations when using
Python expressions or code snippets. The context always has the following builtins available,

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
| pydash            | [pydash](https://pydash.readthedocs.io/en/latest/)                 | Utility libraries for doing “stuff” in a functional way.          |
| networkx          | [networkx](https://networkx.org/documentation/stable/index.html)   | Network analysis package                                          |
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
