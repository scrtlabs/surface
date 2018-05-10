from setuptools import setup, find_packages
import io
import os


here = os.path.abspath(os.path.dirname(__file__))
with io.open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = '\n' + f.read()

setup(
    name='surface',
    version='',
    description='',
    long_description=long_description,
    package_dir={'': 'src'},
    packages=find_packages('src', exclude=('tests', )),
    url='',
    license='',
    author='',
    author_email='',
    # install_requires=['click', 'logbook', 'zmq', 'web3'],
    # test_require=['pytest'],
)