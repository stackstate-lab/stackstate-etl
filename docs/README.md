StackState ETL Documentation
==================

The module is compatible with python 2.7 as defined in `pyproject.toml`.
To generate documentation, the following indirect library upgrade is required.

    pip install importlib_metadata==4.11.3

Build HTML documentation by running:

    ./build.sh
    
The docs will appear in _./build_ directory. These docs can be then copied and committed onthe `gh-pages` branch.
