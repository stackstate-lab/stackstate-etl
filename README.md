# StackState ETL 

A framework that makes 3rd-party data extract, transform and load into the 4T model simpler by using low-code yaml
templates.

See [documentation](https://stackstate-lab.github.io/stackstate-etl/) for more information.


## Installation on StackState Agent 2 for Linux

StackState Agent 2 supports python 2.7.  StackState ETL is transpiled to python 2.7 code.

From a shell on the agent machine run,

```bash 
sudo -H -u stackstate-agent bash -c "/opt/stackstate-agent/embedded/bin/pip install https://github.com/stackstate-lab/stackstate-etl/releases/download/v0.2.0/stackstate-etl-py27-0.2.0.tar.gz"
```

## Development

This project is generated using [Yeoman](https://yeoman.io/) and the [StackState Generator](https://github.com/stackstate-lab/generator-stackstate-lab)

StackState ETL is developed in Python 3, and is transpiled to Python 2.7 for deployment to the StackState Agent v2 environment.

---
### Prerequisites:

- Python v.3.9.x See [Python installation guide](https://docs.python-guide.org/starting/installation/)
- [PDM](https://pdm.fming.dev/latest/#recommended-installation-method)
- [Docker](https://www.docker.com/get-started)
---

### Setup local code repository

```bash 
git clone git@github.com:stackstate-lab/stackstate-etl.git
cd stackstate-etl
pdm install 
```
The `pdm install` command sets up all the projects required dependencies using [PEP 582](https://peps.python.org/pep-0582/) instead of virtual environments.

### Code styling and linting

- [Black](https://black.readthedocs.io/en/stable/) for formatting
- [isort](https://pycqa.github.io/isort/) to sort imports
- [Flakehell](https://flakehell.readthedocs.io/) for linting
- [mypy](https://mypy.readthedocs.io/en/stable/) for static type checking

Appy by running
```bash
pdm format
```

### Running unit tests

```bash
pdm test
```

### Build

The build will transpile the custom agent check to Python 2.7 and creates and install shell script packaged into
the `dist/stackstate-etl-py27-0.2.0.tar.gz`

```bash
pdm build
```

---

## Development

StackState ETL is developed in Python 3, and is transpiled to Python 2.7 during build.

### Prerequisites:

- Python v.3.7+. See [Python installation guide](https://docs.python-guide.org/starting/installation/)
- [Poetry](https://python-poetry.org/docs/#installation)

### Setup local code repository

```bash 
git clone git@github.com:stackstate-lab/stackstate-etl.git
cd stackstate-etl
poetry install 
```

The poetry install command creates a virtual environment and downloads the required dependencies.

### Styling and Linting

- [Black](https://black.readthedocs.io/en/stable/) for formatting
- [isort](https://pycqa.github.io/isort/) to sort imports
- [Flakehell](https://flakehell.readthedocs.io/) for linting
- [mypy](https://mypy.readthedocs.io/en/stable/) for static type checking

Appy by running the shell script,

```bash 
./apply_style.sh
```
---
### Syntax Highlighting

#### VSCode

```bash
cp -r ./grammar/setl-vscode ~/.vscode/extensions
```

#### Intellij

Import the `./grammar/setl-tmbundle`. See [Textmate Bundles](https://www.jetbrains.com/help/idea/textmate.html)

---
### Running in Intellij

Setup the module sdk to point to the virtual python environment created by Poetry.
Default on macos is `~/Library/Caches/pypoetry/virtualenvs`
