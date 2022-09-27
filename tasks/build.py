import subprocess
from pathlib import Path
import toml

PROJECT_DIR = Path(__file__).parent.parent


def get_pyproject():
    return toml.load(Path.joinpath(PROJECT_DIR, "pyproject.toml"))


def main():
    print("Preparing Python 2.7 package...")
    pyproject = get_pyproject()
    prepare_package(pyproject)
    print("Done!")


def prepare_package(pyproject):
    version = pyproject["project"]['version']
    commands = """
    rm -rf build/py27 
    py-backwards -i src -o build/py27 -t 2.7
    sed "s/__version__/%s/" tasks/py27/PKG-INFO > build/py27/PKG-INFO
    sed "s/__version__/%s/" tasks/py27/setup.py > build/py27/setup.py
    cd build/py27
    echo "Building py27 sdist..."
    distname="stackstate-etl-py27-%s.tar.gz"
    tar -czf "../../dist/$distname" *
    echo "Built sdist at dist/$distname"
    cd ../..
    rm -rf build/py27
    """ % (version, version, version)
    subprocess.check_call(commands, shell=True, executable='/bin/bash', cwd=PROJECT_DIR)


if __name__ == "__main__":
    main()


