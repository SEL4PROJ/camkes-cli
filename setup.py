import os
from setuptools import setup, find_packages

package_name = find_packages()[0]
package_path = os.path.join(os.getcwd(), package_name)

templates = []

for (path, _, files) in os.walk(os.path.join(package_path, 'templates')):
    for f in files:
        templates.append(os.path.relpath(os.path.join(path, f), package_path))

setup(
    name='camkes-cli',
    version='0.2.0',
    description='Command line interface for the CAmkES component framework',
    url='https://github.com/seL4proj/camkes-cli',
    license='BSD2',
    author='Stephen Sherratt',
    author_email='Stephen.Sherratt@data61.csiro.au',
    keywords='camkes sel4',
    packages=[package_name],
    install_requires=['jinja2', 'toml', 'pyelftools'],
    entry_points={
        'console_scripts': [
            'camkes-cli=camkes_cli.cli:main',
        ],
    },
    package_data={
        'camkes_cli':templates,
    },
)
