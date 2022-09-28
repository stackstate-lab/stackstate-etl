---
layout: default
title: Getting Started
has_children: false
nav_exclude: false
nav_order: 2
---


# Installation StackState Agent V2

StackState Agent 2 supports python 2.7.  StackState ETL is transpiled to python 2.7 code.

From a shell on the agent machine run,

```bash 
sudo -H -u stackstate-agent bash -c "/opt/stackstate-agent/embedded/bin/pip install https://github.com/stackstate-lab/stackstate-etl/releases/download/v0.2.0/stackstate-etl-py27-0.2.0.tar.gz"

```

#  StackState ETL Command-line Utility


Prepare a virtual environment on your local machine to install the command-line utility.

```bash
$ # Install virtual env
$ pip install virtualenv
$ virtualenv --version
$ # Create a virtual environment in a directory of your choosing 
$ cd project_folder
$ virtualenv venv
$ source venv/bin/activate
```

Now install the `stsetl` utility.

```bash
pip install https://github.com/stackstate-lab/stackstate-etl/releases/download/0.2.0/stackstate-etl-0.2.0.tar.gz
```

The `stsetl` command-line utility reads ETL yaml files specified in the `conf.yaml` and sends the resulting 4T elements
to StackState.

```bash
$ stsetl --help
Usage: stsetl [OPTIONS]

Options:
  -f, --conf  TEXT  Configuration yaml file
  --log-level TEXT  Log Level
  --dry-run         Dry run static topology creation
  --work-dir  TEXT  Set the current working directory
  --help            Show this message and exit.
```

## Configuration

Create a `conf.yaml` similar to the one below. Remember to change the `receiver_url` and `api_key`

```yaml

stackstate:
  receiver_url: https://<your stackstate server>/receiver
  api_key: xxxxx
  #  use as the source identifier and url in StackState integrations when creating a Custom Synchronzation instance.
  instance_type: stackstate_etl
  instance_url: stackstate_etl_demo
  health_sync:
    source_name: elt_health
    stream_id: "etl_health_topo"   # unique id representing this stream instance
    expiry_interval_seconds: 2592000  # 30 Days
    repeat_interval_seconds: 1800     # 30 Minutes
  internal_hostname: localhost

etl:
  refs:
    - "file://./templates"
```

Create a sample template and dry run to see resulting Components, Relations and Health
You can copy [sample_etl.yaml](https://raw.githubusercontent.com/stackstate-lab/stackstate-etl/master/tests/sample_etl.yaml) to `./templates`

```bash
$ mkdir -p ./templates
$ curl -L https://raw.githubusercontent.com/stackstate-lab/stackstate-etl/master/tests/sample_etl.yaml -o ./template/sample_etl.yaml
$ stsetl --dry-run   
```
