from setuptools import setup

setup(
    name='crly',
    version='v0.1.1',
    packages=['crly'],
    python_requires='>3.5.2',
    install_requires=['bs4', 'docopt', 'tinydb', 'dotmap', 'python-dateutil'],
    entry_points={'console_scripts': ['crly = crly.__main__:main']})
