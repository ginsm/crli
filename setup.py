from setuptools import setup

setup(name='crly',
      version='v0.2.3',
      packages=['crly'],
      python_requires='>3.5.2',
      install_requires=[
          'bs4', 'docopt', 'tinydb', 'dotmap', 'python-dateutil', 'colorama'
      ],
      entry_points={'console_scripts': ['crly = crly.__main__:main']})
