---
layout: default
title: Pre- Post- Processors
parent: Concepts
nav_order: 6
---

# Pre- and Post- Processors

At times you may need to define utility functions for use by templates, or you may want to process all
components in the factory after all queries in the ETL definition have been executed. Adding common labels for example.
Pre- / Post-processors can be used for these cases. Note that these are scoped to running only within
the ETL definition they are found in. Processors can use [Scopes](#scopes) to contribute functions.


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

The example above shows a conversion function that can convert bytes to kilobytes, gigabytes, etc.
Any code expression can access this function to perform the conversion.

```yaml
value: "|global_session['bytesto'](item['usage_stats']['storage.logical_usage_bytes'], 'g')"
```

## Scopes

A `session` scope and a `global_session` scope is available. `session` is only valid with the ETL definition.



