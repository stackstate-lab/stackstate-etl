# -*- coding: utf-8 -*-
from setuptools import setup
packages = [
    'stackstate_etl',
    'stackstate_etl.cli',
    'stackstate_etl.etl',
    'stackstate_etl.model',
    'stackstate_etl.stackstate',
]
package_data = {'': ['*']}
install_requires = [
    'PyYAML==5.4.1',
    'asteval==0.9.17',
    'attrs>=21.4.0,<22.0.0',
    'cachetools==3.1.1',
    'click<8.0',
    'importlib-resources==3.3.1',
    'jsonpath-ng>=1.5.3,<2.0.0',
    'pandas==0.24.2',
    'pydash==4.9.3',
    'pytz>=2022.1,<2023.0',
    'requests==2.25.0',
    'schematics>=2.1.1,<3.0.0',
    'six>=1.16.0,<2.0.0',
    'networkx==2.2',
    'pendulum>=2.1.2,<2.2.0'
]
setup_kwargs = {
   'name': 'stackstate-etl',
   'version': '__version__',
   'description': 'StackState Extract-Transform-Load Framework for 4T data ingestion',
   'long_description': 'None',
   'author': 'Ravan Naidoo',
   'author_email': 'rnaidoo@stackstate.com',
   'maintainer': 'None',
   'maintainer_email': 'None',
   'url': 'None',
   'packages': packages,
   'package_data': package_data,
   'install_requires': install_requires,
   'python_requires': '>=2.7, <=2.8',
}

setup(**setup_kwargs)
