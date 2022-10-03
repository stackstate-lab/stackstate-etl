---
layout: default
title: Getting Started
has_children: false
nav_exclude: false
nav_order: 2
---

# Run Yo Code

The [stackstate-lab](https://github.com/stackstate-lab/generator-stackstate-lab) [Yeoman](http://yeoman.io) generator can
scaffold a new StackState Agent Check project using the [StackState ETL Framework](https://github.com/stackstate-etl/).
The Yeoman generator will walk you through the steps required to create your project prompting for the required information.

To launch the generator simply type:

```bash
yo stackstate-lab --useEtlFramework 
```

## StackState Agent Check Project 

The generated project uses [PDM](https://pdm.fming.dev/) for Python package and dependency management which 
supports the latest PEP standards. Especially [PEP 582 support](https://www.python.org/dev/peps/pep-0582), no virtualenv involved at all.
[PDM Scripts](https://pdm.fming.dev/latest/usage/scripts/) drive the development life-cycle of the project.

| Command        | Description                                                                                                                |
|----------------|----------------------------------------------------------------------------------------------------------------------------|
| pdm install    | Installs package and setups up PEP 582 environment                                                                         |
| pdm test       | Runs unit tests                                                                                                            |
| pdm format     | Code styling and linting performed by Black, FlakeHell and MyPy                                                            |
| pdm build      | Will transpile the custom agent check to Python 2.7 and create install zip                                                 |
| pdm cleanAgent | Remove the custom StackState Agent Docker image used during development                                                    |
| pdm buildAgent | Build a custom [StackState Agent Docker](https://hub.docker.com/r/stackstate/stackstate-agent-2) to use during development |
| pdm check      | Dry-run custom agent check inside the StackState Agent container                                                           |
| pdm serve      | Starts the StackState Agent in the foreground using the configuration `src/data/conf.d/` directory                         |


# Installation on StackState Agent V2

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
