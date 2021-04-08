from setuptools import setup

setup(
    name='crli',
    version='v0.1.0',
    packages=['crli'],
    python_requires='>3.5.2',
    install_requires=['bs4', 'docopt', 'tinydb', 'dotmap', 'python-dateutil'],
    entry_points={'console_scripts': ['crli = crli.__main__:main']})
