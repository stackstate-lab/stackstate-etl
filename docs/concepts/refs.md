---
layout: default
title: Refs
parent: Concepts
nav_order: 5
---


# Refs

Multiple ETL definition files can easily be composed using `refs` target definitions can be in directories or in python
modules. Nested `refs` are allowed. ETL definitions are executed in the order they are loaded in.
When the ref points to a folder, alphabetical order is applied to yamls before loading.


```yaml
etl:
  refs:
    - "module_dir://sts_nutanix_impl.templates"
  ...
```

`refs` is a list of paths referencing other ETL definitions. The paths have the format of `<prefix>://<dir or file>`

| Prefix      | Description                                     |
|-------------|-------------------------------------------------|
| module_dir  | reads all yaml files from a python module       |
| module_file | reads yaml file from a python module            |
| file        | reads yaml file(s) from location on file system |
