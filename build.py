from py_backwards import const, exceptions, messages
from py_backwards.compiler import compile_files
import re
from os.path import join
import shutil


def build(setup_kwargs):
    _build(setup_kwargs, "py27")
    _build(setup_kwargs, "py3", enable_py_backward=False)


def _build(setup_kwargs, py_ver_name, enable_py_backward=True):
    build_dir = join("build", f"lib_{py_ver_name}")
    pkg_dir = join(build_dir, f"{setup_kwargs['name']}-{setup_kwargs['version']}")
    target_dir = join(pkg_dir, "stackstate_etl")
    shutil.rmtree(build_dir, ignore_errors=True)
    src_dir = "stackstate_etl"

    if enable_py_backward:
        # Copy resources in python package
        ignore_py_files = shutil.ignore_patterns("*.py")
        shutil.copytree(
            src_dir, target_dir, ignore=ignore_py_files
        )
        _compile_to_py27(src_dir, target_dir)
    else:
        shutil.copytree(
            src_dir, target_dir
        )

    _generate_setup_py(setup_kwargs, pkg_dir)
    _generate_pkg_info(setup_kwargs, pkg_dir)

    zipfile = f"{setup_kwargs['name']}-{py_ver_name}-{setup_kwargs['version']}"
    shutil.make_archive(join("dist", zipfile), "gztar", pkg_dir)
    print(f"Built {zipfile}.tar.gz")
    return 0


def _generate_pkg_info(setup_kwargs, target_dir):
    code = ["Metadata-Version: 2.1", f"Name: {setup_kwargs['name']}", f"Version: {setup_kwargs['version']}",
            f"Summary: {setup_kwargs['description']}", f"Author: {setup_kwargs['author']}",
            f"Author-email: {setup_kwargs['author_email']}", f"Requires-Python: {setup_kwargs['python_requires']}",
            "Classifier: Programming Language :: Python :: 2", "Classifier: Programming Language :: Python :: 3"]
    pattern = re.compile("([A-Za-z-]*)([=><@].*)")
    for req in setup_kwargs["install_requires"]:
        match = pattern.match(req)
        if match:
            code.append(f"Requires-Dist: {match.group(1)} ({match.group(2)})")
    with (open(join(target_dir, "PKG-INFO"), mode="w")) as f:
        f.write("\n".join(code))


def _generate_setup_py(setup_kwargs, target_dir):
    code = ["# -*- coding: utf-8 -*-", "from setuptools import setup", "packages = ["]
    for pkg in setup_kwargs["packages"]:
        code.append(f"    '{pkg}',")
    code.append("]")
    code.append("package_data = {'': ['*']}")
    code.append("install_requires = [")
    for req in setup_kwargs["install_requires"]:
        code.append(f"    '{req}',")
    code.append("]")
    code.append("setup_kwargs = {")
    code.append(f"   'name': '{setup_kwargs['name']}',")
    code.append(f"   'version': '{setup_kwargs['version']}',")
    code.append(f"   'description': '{setup_kwargs['description']}',")
    code.append(f"   'long_description': '{setup_kwargs['long_description']}',")
    code.append(f"   'author': '{setup_kwargs['author']}',")
    code.append(f"   'author_email': '{setup_kwargs['author_email']}',")
    code.append(f"   'maintainer': '{setup_kwargs['maintainer']}',")
    code.append(f"   'maintainer_email': '{setup_kwargs['maintainer_email']}',")
    code.append(f"   'url': '{setup_kwargs['url']}',")
    code.append("   'packages': packages,")
    code.append("   'package_data': package_data,")
    code.append("   'install_requires': install_requires,")
    code.append(f"   'python_requires': '{setup_kwargs['python_requires']}',")
    code.append("}")
    code.extend(["", "setup(**setup_kwargs)", ""])
    with (open(join(target_dir, "setup.py"), mode="w")) as f:
        f.write("\n".join(code))


def _compile_to_py27(src_dir, target_dir) -> None:
    try:
        print(f"Compiling files in {src_dir}  to {target_dir}")
        result = compile_files(
            src_dir, target_dir, const.TARGETS["2.7"]
        )
        if result.files == 0:
            print("No python files found to compile.")
            raise Exception("Stopping because no custom checks found to compile")
        print(messages.compilation_result(result))
    except exceptions.CompilationError as e:
        print(messages.syntax_error(e))
        raise e
    except exceptions.TransformationError as e:
        print(messages.transformation_error(e))
        raise e
    except PermissionError as e:
        print(messages.permission_error(target_dir))
        raise e
