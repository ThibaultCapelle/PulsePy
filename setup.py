from setuptools import setup
import os

def package_files(directory):
    paths = []
    for (path, directories, filenames) in os.walk(directory):
        for filename in filenames:
            paths.append(os.path.join('..', path, filename))
    return paths

extra_files = package_files(os.path.join('PulsePy', 'fpga'))

setup(name='PulsePy',
      version='1.0',
      packages=['PulsePy'],
      package_dir={
        'PulsePy': 'PulsePy',
      },
      package_data={'': extra_files}
      )
